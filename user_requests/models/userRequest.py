from django.db import models
from core.models import User
from django.db.models import Q
from shifts.models import Shift
from django.utils import timezone
from user_requests.models.notifications import Notification


class IncludeRequestData(models.Model):
    """Helper model to store extra data for INCLUDE requests."""
    user_request = models.OneToOneField('UserRequest', on_delete=models.CASCADE, related_name='include_data')
    center = models.ForeignKey('shifts.Center', on_delete=models.CASCADE)
    month = models.ForeignKey('shifts.Month', on_delete=models.CASCADE)
    day = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['center', 'month', 'day']),
        ]


class UserRequest(models.Model):
    class RequestType(models.TextChoices):
        DONATION = 'donation', 'Doação'
        EXCHANGE = 'exchange', 'Troca'
        INCLUDE = 'include', 'Incluir'
        EXCLUDE = 'exclude', 'Excluir'

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

    def __str__(self):
        return f"{self.request_type} requested by {self.requester}"
    
    @property
    def center(self):
        """The center object associated with this request."""
        if self.shift:
            return self.shift.center
        elif self.request_type == self.RequestType.INCLUDE and hasattr(self, 'include_data'):
            return self.include_data.center
        return None
    
    @property
    def date(self):
        if self.shift:
            return self.shift.get_date()
        elif self.request_type == self.RequestType.INCLUDE and hasattr(self, 'include_data'):
            return Shift.gen_date(self.include_data.month, self.include_data.day)
        return None
    
    @property
    def month(self):
        """The month object associated with this request."""
        if self.shift:
            return self.shift.month
        elif self.request_type == self.RequestType.INCLUDE and hasattr(self, 'include_data'):
            return self.include_data.month
        return None
    
    @property
    def day(self):
        return self.date.day if self.date else None
    
    @property
    def target(self):
        """The user who is the target of this request (donor/donee/excludee/includee)"""
        if self.request_type == self.RequestType.DONATION:
            return self.requestee
        elif self.request_type == self.RequestType.EXCLUDE:
            return self.donor
        elif self.request_type == self.RequestType.INCLUDE:
            return self.donee
        return None
    
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

    def accept(self, responder):
        if not (responder == self.requestee) and not responder.is_superuser:
            raise PermissionError("Only the requestee or admins(superusers) can accept a donation request.")
        
        conflict = Shift.check_conflict(self.donee,
                                        self.month,
                                        self.day,
                                        self.start_hour,
                                        self.end_hour)
        if (not self.request_type == self.RequestType.EXCLUDE) and conflict:
            self.refuse(responder)
            self.notify_conflict(conflict)
            return
        
        self.responder = responder
        if self.request_type == self.RequestType.DONATION:
            if not (self.shift and self.donor) or not self.shift.user == self.donor:
                raise ValueError("The donor must be the current assignee of the shift.")
            
            new_shift = self.shift.split(self.start_hour, self.end_hour)
            new_shift.change_user(self.donee)

        # INCLUDE: donee = user to be included 
        elif self.request_type == self.RequestType.INCLUDE:
            
            new_shift = Shift.add(
                doctor=self.donee,
                center=self.center,
                month=self.month,
                day=self.day,
                start_time=self.start_hour,
                end_time=self.end_hour
            )

        # EXCLUDE: donor = user to be excluded
        elif self.request_type == self.RequestType.EXCLUDE:
            if not (self.shift and self.donor) or not self.shift.user == self.donor:
                raise ValueError("The excludee must be the current assignee of the shift.")

            # self.remove_notifications()
            # self.notify_response("accept") seems redundant here
            to_delete_shift = self.shift.split(self.start_hour, self.end_hour)
            to_delete_shift.delete()

            # No need to delete other requests on same shift
            # as they are supposed to be cascaded by shift deletion

        self.close()

        self.is_approved = True
        self.save(update_fields=['is_approved'])

        self.remove_notifications()
        self.notify_response("accept")

    
    def refuse(self, responder):
        self.responder = responder
        self.close()
        self.remove_notifications()

        self.notify_response("refuse")

    def cancel(self, canceller):
        self.responder = canceller
        self.close()
        self.remove_notifications()

    def invalidate(self):
        """Mark as invalid (e.g. if shift is deleted or change users)"""
        self.close()
        self.remove_notifications()

    def close(self):
        """Close without action (e.g. if request is fulfilled outside the system)"""
        self.is_open = False
        self.closing_date = timezone.now()
        self.save(update_fields=['is_open', 'closing_date'])

    def remove_notifications(self):
        """Archive related notifications"""
        related_notifications = Notification.objects.filter(
            related_ct__model='userrequest',
            related_id=str(self.pk),
            is_deleted=False
        )
        related_notifications.update(is_deleted=True)

    def notify_conflict(self, conflict_shift):
        from . import Notification
        Notification.notify_conflict(self, conflict_shift)
    
    def notify_response(self, response):
        from . import Notification
        Notification.notify_response(self, response)

    def notify_request(self):
        from . import Notification
        Notification.notify_request(self)
