from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from user_requests.models.notifications import Notification
from .serializers import NotificationSerializer
from django.db import models


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return Notification.objects.filter(is_deleted=False).order_by('-created_at')
        
        if user.is_superuser:
            return Notification.objects.filter(
                models.Q(receiver__isnull=True) | models.Q(receiver=user),
                is_deleted=False
            )
        
        return Notification.objects.filter(
            receiver=user, is_deleted=False
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        notif = self.get_object()
        response = request.data.get('action')

        print("response:", response)
        
        if response == 'accept':
            # TODO: implement accept logic
            # notif.related_obj.accept(request.user)  # assuming related_obj is a UserRequest
            # notif.archive()  # mark notification as deleted
            pass
        elif response == 'refuse':
            notif.related_obj.refuse(request.user)  # assuming related_obj is a UserRequest
            notif.archive()  # mark notification as deleted
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()  # call your model’s helper method
        notif.save(update_fields=['is_read', 'seen_at'])
        return Response(self.get_serializer(notif).data, status=status.HTTP_200_OK)
