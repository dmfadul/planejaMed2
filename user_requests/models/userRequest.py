from django.db import models
from core.models import User
from shifts.models import Shift


class AbstractUserRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_made')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_responded', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    closing_date = models.DateTimeField(null=True, blank=True)
    action = models.CharField(max_length=20)

    class Meta:
        abstract = True


class DonationRequest(AbstractUserRequest):
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_received', null=True, blank=True)
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_made', null=True, blank=True)
    donee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_received', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='donation_requests', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.action = 'donation'
        super().save(*args, **kwargs)
