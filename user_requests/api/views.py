from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from user_requests.models.notifications import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Notification.objects.filter(is_deleted=False).order_by('-created_at')
        elif user.is_superuser:
            return Notification.objects.none()
        return Notification.objects.filter(
            receiver=user, is_read=False
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        notif = self.get_object()
        # custom logic to handle a response (e.g. accept/decline)
        # return an appropriate result (e.g. status 204)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()  # call your model’s helper method
        notif.save(update_fields=['is_read', 'seen_at'])
        return Response(self.get_serializer(notif).data, status=status.HTTP_200_OK)
