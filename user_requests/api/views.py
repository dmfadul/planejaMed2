from datetime import datetime
from django.utils import timezone
from django.db import models, transaction
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from user_requests.services import create_user_request
from rest_framework import viewsets, permissions, status
from user_requests.models.notifications import Notification
from user_requests.models import UserRequest
from django.contrib.contenttypes.models import ContentType
from .serializers import (
    NotificationSerializer,
    VacationRequestSerializer,
    IncomingUserRequestSerializer,
    OutUserRequestSerializer
)


class UserRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        ser = IncomingUserRequestSerializer(
            data=request.data,
            context={"request": request}
        )

        ser.is_valid(raise_exception=True)

        # normalized, typed, DB-ready params:
        params = ser.validated_data
        req_obj = create_user_request(**params)

        out = OutUserRequestSerializer(req_obj)
        return Response(out.data, status=status.HTTP_201_CREATED)
    

class VacationRequest(APIView):
    def post(self, request):
        mode = request.data.get("mode", "solicitation")
        request_type = request.data.get("type")
        start_date = datetime.strptime(request.data.get("startDate"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.data.get("endDate"), "%Y-%m-%d").date()

        payload = {
            "request_type": request_type,
            "start_date": start_date,
            "end_date": end_date,
        }

        serializer = VacationRequestSerializer(
            data=payload,
            context={
                "request": request,
                "mode": mode
            }
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            instance = serializer.save(requester=request.user)
            instance.notify_request()

            if mode == "registry":
                instance.approve(request.user)

        return Response({"message": "Vacation request created"}, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        qs = Notification.objects.filter(
            Q(expires_at__isnull=True) |
            Q(expires_at__gt=timezone.now()),
            is_deleted=False,
        )

        if user.is_staff or user.is_superuser:
            return qs.exclude(
                Q(kind__in=["mass_action", "cancel", "info"]) &
                Q(receiver__isnull=False) &
                ~Q(receiver=user)
            ).order_by("-created_at")
        
        if user.is_director:
            request_ids = UserRequest.objects.filter(
                request_type__in=[
                    UserRequest.RequestType.INCLUDE,
                    UserRequest.RequestType.EXCLUDE,
                ]
            ).values_list("id", flat=True)
        
            request_content_type = ContentType.objects.get_for_model(UserRequest)
        
            return qs.filter(
                Q(receiver=user) |
                (
                    Q(
                        related_ct=request_content_type,
                        related_id__in=request_ids,
                    )
                    & ~Q(kind__in=["info", "cancel", "mass_action"])
                )
            ).distinct().order_by("-created_at")
        
        
        return qs.filter(receiver=user).order_by("-created_at")
    
    def get_serializer_context(self):
        """Pass viewer_id to serializer for rendering logic."""
        context = super().get_serializer_context()
        context['viewer_id'] = self.request.user.id
        return context

    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        notif = self.get_object()
        response_action = request.data.get("action")

        if response_action == "accept":
            result = notif.related_obj.accept(request.user)

            if result:
                return Response(
                    {"error": result.get("error")},
                    status=status.HTTP_409_CONFLICT,
                )

            notif.archive()
            message = "Requisição aceita com sucesso."

        elif response_action == "refuse":
            notif.related_obj.refuse(request.user)
            notif.archive()
            message = "Requisição recusada com sucesso."

        elif response_action == "cancel":
            notif.related_obj.cancel(request.user)
            notif.archive()
            message = "Requisição cancelada com sucesso."

        else:
            return Response(
                {"error": "Ação inválida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": message},
            status=status.HTTP_200_OK,
        )
    
    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()  # call your model’s helper method
        notif.save(update_fields=['is_read', 'seen_at'])
        return Response(self.get_serializer(notif).data, status=status.HTTP_200_OK)
