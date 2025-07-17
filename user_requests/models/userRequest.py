from django.db import models
from core.models import User


class AbstractUserRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_made')
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    closing_date = models.DateTimeField(null=True, blank=True)
    action = models.CharField(max_length=20)

    class Meta:
        abstract = True


class DonationRequest(AbstractUserRequest):
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_received')

    def save(self, *args, **kwargs):
        self.action = 'donation'
        super().save(*args, **kwargs)
