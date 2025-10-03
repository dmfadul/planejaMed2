from django.db import models
from core.models import User
from django.db.models import Q
from shifts.models import Shift
from django.utils import timezone
from user_requests.models.notifications import Notification



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

        if self.request_type == self.RequestType.DONATION:
            if not (self.responder == self.requestee) and not self.responder.is_staff:
                raise PermissionError("Only the requestee or staff can accept a donation request.")

            if not (self.shift and self.donor) or not self.shift.user == self.donor:
                raise ValueError("The donor must be the current assignee of the shift.")

            # check if donne is available (no overlapping shifts)
            # if not, refuse automatically and notify
            
            # new_shift = self.shift.split(self.start_hour, self.end_hour, new_user=self.donee)
            # conflict = new_shift.change_user(self.donee)
            
            # if conflict:
                # self.refuse(responder) # send notification about refusal due to conflict
            # Notify both parties about the successful donation
        else:
            # check for conflicts
            # check for other requests on same shift and hours
            # if there are, refuse them automatically
            pass

        self.is_open = False
        self.is_approved = True
        self.responder = responder
        self.closing_date = timezone.now()
        self.save(update_fields=['is_open', 'is_approved', 'responder', 'closing_date'])
        self.remove_notifications()
    
    def refuse(self, responder):
        self.is_open = False
        self.is_approved = False
        self.responder = responder
        self.closing_date = timezone.now()
        self.save(update_fields=['is_open', 'is_approved', 'responder', 'closing_date'])
        self.remove_notifications()
        
        # TODO: send notification to requester about refusal

    def remove_notifications(self):
        """Archive related notifications"""
        related_notifications = Notification.objects.filter(
            related_ct__model='userrequest',
            related_id=str(self.pk),
            is_deleted=False
        )

        related_notifications.update(is_deleted=True)

    def notify_response(self, response):
        # TODO: implement notification logic based on response type
        if response == "accept":
            pass
        elif response == "refuse":
            pass
        elif response == "cancel":
            pass
        else:
            print("Response:", response)
            raise ValueError("Invalid response type for notification.")

    def notify_request(self):
        if self.request_type == self.RequestType.DONATION and self.donor == self.requester:
            temp_key = f'request_pending_donation_offered'
        elif self.request_type == self.RequestType.DONATION and self.donee == self.requester:
            temp_key = f'request_pending_donation_required'
        else:
            temp_key = f'request_pending_{self.request_type}'

        # Notify the requestee
        Notification.from_template(
            template_key=temp_key,
            sender=self.requester,
            receiver=self.requestee,
            context={
                'sender_name': self.requester.name,
                'receiver_id': self.requestee.id,
                'shift_center': self.shift.center.abbreviation,
                'shift_date': self.shift.get_date().strftime("%d/%m/%y"),
                'start_hour': f"{self.start_hour:02d}:00",
                'end_hour': f"{self.end_hour:02d}:00",
            },
            related_obj=self,
        )
  
        # Send cancelable notification to requester
        Notification.from_template(
            template_key='request_received',
            sender=self.requester,
            receiver=self.requester,
            context={
                'requestee_name': self.requestee.name,
                'request_type': self.get_request_type_display().upper(),
                'shift_center': self.shift.center.abbreviation,
                'shift_date': self.shift.get_date().strftime("%d/%m/%y"),
                'start_hour': f"{self.start_hour:02d}:00",
                'end_hour': f"{self.end_hour:02d}:00",
            },
            related_obj=self,
        )
