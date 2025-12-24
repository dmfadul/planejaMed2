from django.db import models
from core.models import User
from django.utils import timezone
from vacations.models import Vacation
from user_requests.models.notifications import Notification


class VacationRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests_received', null=True, blank=True)
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests_responded', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    closing_date = models.DateTimeField(null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()
    request_type = models.CharField(max_length=20, choices=Vacation.VacationType.choices)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Vacation request by {self.requester} from {self.start_date} to {self.end_date}"
    
    @property
    def target(self):
        return self.requester

    def accept(self, responder):
        if not responder.is_superuser:
            raise PermissionError("Only admins(superusers) can accept vacation requests.")
        
        vacation = Vacation.create_vacation(
            user=self.requester,
            start_date=self.start_date,
            end_date=self.end_date,
            vacation_type=self.request_type
        )
        if vacation == -1:
            self.refuse(responder)
            return -1  # Indicate conflict

        self.close()
        self.is_approved = True
        self.responder = responder
        self.save(update_fields=['is_approved', 'responder'])

        self.remove_notifications()
        self.notify_response("accept")

        return True

    def refuse(self, responder):
        if not responder.is_superuser:
            raise PermissionError("Only admins(superusers) can refuse vacation requests.")
        
        self.responder = responder
        self.close()
        self.save(update_fields=['responder'])
        self.remove_notifications()

        self.notify_response("refuse")

        return True

    def cancel(self, cancellor):
        if not cancellor == self.requester:
            raise PermissionError("Only the requester can cancel their vacation request.")
        
        self.responder = cancellor # TODO: check if responder really saves or if needs save call
        self.close()
        self.remove_notifications()

        return True

    def close(self):
        """Close without action (e.g. if request is fulfilled outside the system)"""
        self.is_open = False
        self.closing_date = timezone.now()
        self.save(update_fields=['is_open', 'closing_date'])

    def remove_notifications(self):
        """Archive related notifications"""
        related_notifications = Notification.objects.filter(
            related_ct__model='vacationrequest',
            related_id=str(self.pk),
            is_deleted=False
        )
        related_notifications.update(is_deleted=True)

    def notify_request(self):
        Notification.notify_request(self)

    def notify_response(self, response):
        Notification.notify_vacation_response(self, response)