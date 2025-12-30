from datetime import datetime
from django.db import models
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from user_requests.services import create_user_request
from rest_framework import viewsets, permissions, status
from user_requests.models.notifications import Notification
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
        
        if user.is_staff or user.is_superuser:
            return Notification.objects.filter(is_deleted=False).order_by('-created_at')
        
        # if user.is_superuser:
        #     return Notification.objects.filter(
        #         models.Q(receiver__isnull=True) | models.Q(receiver=user),
        #         is_deleted=False
        #     )
        
        return Notification.objects.filter(
            receiver=user, is_deleted=False
        ).order_by('-created_at')
    
    def get_serializer_context(self):
        """Pass viewer_id to serializer for rendering logic."""
        context = super().get_serializer_context()
        context['viewer_id'] = self.request.user.id
        return context

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        notif = self.get_object()
        response = request.data.get('action')
        
        # assuming related_obj is a UserRequest
        if response == 'accept':
            flag = notif.related_obj.accept(request.user)
            notif.archive()
            if flag == -1:
                return Response({'error': 'Vacation request conflicts with existing vacations.'}, status=status.HTTP_409_CONFLICT)
        elif response == 'refuse':
            notif.related_obj.refuse(request.user)
            notif.archive()
        elif response == 'cancel':
            notif.related_obj.cancel(request.user)  
            notif.archive()
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()  # call your model’s helper method
        notif.save(update_fields=['is_read', 'seen_at'])
        return Response(self.get_serializer(notif).data, status=status.HTTP_200_OK)
