from django.db import models
from core.models import User
from vacations.models import Vacation


class VacationRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests_made')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests_received', null=True, blank=True)
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests_responded', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    closing_date = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=Vacation.VacationType.choices)