from django.db import models
from core.models import User
from django.db.models import Q
from shifts.models import Shift


class UserRequest(models.Model):
    class RequestType(models.TextChoices):
        DONATION = 'donation', 'Donation'
        EXCHANGE = 'exchange', 'Exchange'
        INCLUDE = 'include', 'Include'
        EXCLUDE = 'exclude', 'Exclude'

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_made')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_received', null=True, blank=True)
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_responded', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    closing_date = models.DateTimeField(null=True, blank=True)

    # What kind of request this is
    request_type = models.CharField(max_length=20, choices=RequestType.choices)

    # Common payload (shift/time window)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='user_requests', null=True, blank=True)
    start_hour = models.IntegerField(null=True, blank=True)
    end_hour = models.IntegerField(null=True, blank=True)

    # Role fields (all optional; validation will enforce per type)
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_made', null=True, blank=True)
    donee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_received', null=True, blank=True)

    class Meta:
        constraints = [
            # one open request per requester / type / shift
            models.UniqueConstraint(
                fields=['requester', 'request_type', 'shift', 'start_hour', 'end_hour'],
                condition=Q(is_open=True),
                name='uniq_open_request_per_requester_type_shift',
            ),
        ]
        indexes = [
            models.Index(fields=['requester', 'is_open', 'created_at']),
            models.Index(fields=['responder', 'is_approved', 'created_at']),
            models.Index(fields=['request_type', 'created_at']),
        ]
        ordering = ['-created_at']

    def clean(self):
        # Minimal per-type rules; adjust to your business logic
        if self.request_type == self.RequestType.DONATION:
            missing = [f for f in ('donor', 'donee', 'shift') if getattr(self, f) is None]
            if missing:
                from django.core.exceptions import ValidationError
                raise ValidationError({m: "This field is required for a donation." for m in missing})

    def save(self, *args, **kwargs):
        # Ensure clean() runs in code paths that bypass forms/serializers
        self.full_clean(exclude=None)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_type} requested by {self.requester}"
