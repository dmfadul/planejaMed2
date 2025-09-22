from django.db import models
from core.models import User

class Notification(models.Model):
    KIND_CHOICES = [('action','action'), ('info','info'), ('error','error')]

    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)   # optional but handy
    is_deleted = models.BooleanField(default=False)         # optional “archive”

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"Notification to {self.receiver.username}: {self.title}"
