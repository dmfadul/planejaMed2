from django.db import models
from core.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    class Kind(models.TextChoices):
        ACTION = 'action', 'Action'
        INFO = 'info', 'Info'
        ERROR = 'error', 'Error'

    # High-level category (visual style/badge color)
    kind = models.CharField(max_length=20, choices=Kind.choices)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')

    # Template machinery
    template_key = models.CharField(max_length=50, null=True, blank=True)
    context = models.JSONField(default=dict, blank=True)

    # Optional linkage to any domain object (UserRequest, Shift, etc.)
    related_ct = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    related_id = models.CharField(max_length=64, null=True, blank=True)
    related_obj = GenericForeignKey('related_ct', 'related_id')
    
    # Rendered fields (what you actually show in the UI)
    title = models.CharField(max_length=120)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)   # optional but handy
    is_deleted = models.BooleanField(default=False)         # optional “archive”

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'is_read', 'is_deleted', 'created_at']),
            models.Index(fields=['template_key']),
            models.Index(fields=['related_ct', 'related_id']),
        ]

    def __str__(self):
        return f"Notification to {self.receiver.username}: {self.title}"


# ------------------- Template Registry ---------------------------------
# Placeholders correspond to context keys

    TEMPLATE_REGISTRY = {
        'request_received': {
            'kind': Kind.ACTION,
            'title': "Nova solicitação de {{ requester_name }}",
            'body': "",
        },


    }
