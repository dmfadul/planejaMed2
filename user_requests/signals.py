# user_requests/signals.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from user_requests.models import UserRequest
from user_requests.models.notifications import Notification


@receiver(pre_delete, sender=UserRequest)
def archive_notifications_on_userrequest_delete(sender, instance: UserRequest, using, **kwargs):
    """
    When a UserRequest is deleted (including via cascade from Shift deletion),
    archive any notifications that point to it via GenericForeignKey.
    """
    ct = ContentType.objects.get_for_model(UserRequest)
    Notification.objects.using(using).filter(
        related_ct=ct,
        related_id=str(instance.pk),
        is_deleted=False,
    ).update(is_deleted=True)
