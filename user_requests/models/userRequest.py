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
            raise PermissionError("Only the requestee or staff can accept a donation request.")
        
        self.responder = responder
        if self.request_type == self.RequestType.DONATION:
            if not (self.shift and self.donor) or not self.shift.user == self.donor:
                raise ValueError("The donor must be the current assignee of the shift.")
            
            conflict = Shift.check_conflict(self.donee,
                                            self.shift.month,
                                            self.shift.day,
                                            self.start_hour,
                                            self.end_hour)
            if conflict:
                self.refuse(responder)
                self.notify_conflict(conflict)
                return

            new_shift = self.shift.split(self.start_hour, self.end_hour)
            new_shift.change_user(self.donee)
            self.notify_response("accept")

        elif self.request_type == self.RequestType.INCLUDE:
            # TODO: implement INCLUDE logic
            
            # check for conflicts
            # create shift
            # notify 
            pass
        elif self.request_type == self.RequestType.EXCLUDE:
            # In EXCLUDE, donee = user to be excluded
            if not (self.shift and self.donee) or not self.shift.user == self.donee:
                raise ValueError("The excludee must be the current assignee of the shift.")

            self.remove_notifications()
            self.notify_response("accept")
            to_delete_shift = self.shift.split(self.start_hour, self.end_hour)
            to_delete_shift.delete()

            # No need to delete other requests on same shift
            # as they are supposed to be cascaded by shift deletion

        self.close()
        self.is_approved = True
        self.save(update_fields=['is_approved'])
        self.remove_notifications()
    
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

    # TODO: move to notifications.py and improve messages
    def notify_conflict(self, conflict_shift):
        # Notify the requester about the conflict
        Notification.from_template(
            template_key="conflict_found",
            sender=self.responder,
            receiver=self.requester,
            context={
                'requester_name': self.requester.name,
                'requestee_name': self.requestee.name if self.requestee else "Admin",
                'donee_name': self.donee.name,
                'conflict_abbr': conflict_shift.center.abbreviation,
                'conflict_day': conflict_shift.get_date().strftime("%d/%m/%y"),
            },
            related_obj=self,
        )        


    def notify_response(self, response):
        # Notify the requester about the response
        was_solicited = ((self.request_type == self.RequestType.DONATION) and
                         (self.donee == self.requestee))
        ctx={
            'sender_name':    self.responder.name,
            'receiver_id':    self.requester.id,
            'response':       "ACEITOU" if response == "accept" else "NEGOU",
            'verb':           "SOLICITAÇÃO" if was_solicited else "OFERTA",
            'req_type':       self.get_request_type_display().upper(),
            'shift_center':   self.shift.center.abbreviation,
            'shift_date':     self.shift.get_date().strftime("%d/%m/%y"),
            'start_hour':     f"{self.start_hour:02d}:00",
            'end_hour':       f"{self.end_hour:02d}:00",
        }

        Notification.from_template(
            template_key="request_responded",
            sender=self.responder,
            receiver=self.requester,
            context=ctx,
            related_obj=self,
        )

        # Do I need to add Cancelable notification to requester?

    def notify_request(self):
        ctx={
            'sender_name':  self.requester.name,
            'receiver_id':  self.requestee.id if self.requestee else None,
            'shift_center': self.shift.center.abbreviation,
            'shift_date':   self.shift.get_date().strftime("%d/%m/%y"),
            'start_hour':   f"{self.start_hour:02d}:00",
            'end_hour':     f"{self.end_hour:02d}:00",
        }

        if self.request_type == self.RequestType.DONATION and self.donor == self.requester:
            temp_key = f'request_pending_donation_offered'
        elif self.request_type == self.RequestType.DONATION and self.donee == self.requester:
            temp_key = f'request_pending_donation_asked_for'
        elif self.request_type == self.RequestType.EXCLUDE:
            temp_key = f'request_pending_exclusion'
            ctx['excludee_name'] = self.shift.user.name
        else:
            temp_key = f'request_pending_{self.request_type}'
        
        
        # TODO: add INCLUDE cases


        # Notify the requestee
        Notification.from_template(
            template_key=temp_key,
            sender=self.requester,
            receiver=self.requestee,
            context=ctx,
            related_obj=self,
        )
  
        # Send cancelable notification to requester
        Notification.from_template(
            template_key='request_received',
            sender=self.requester,
            receiver=self.requester,
            context={
                'requestee_name':   self.requestee.name if self.requestee else self.donee.name,
                'request_type':     self.get_request_type_display().upper(),
                'shift_center':     self.shift.center.abbreviation if self.shift else "N/A",
                'shift_date':       self.shift.get_date().strftime("%d/%m/%y") if self.shift else "N/A",
                'start_hour':       f"{self.start_hour:02d}:00",
                'end_hour':         f"{self.end_hour:02d}:00",
            },
            related_obj=self,
        )
