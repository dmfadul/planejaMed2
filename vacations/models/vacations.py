from django.db import models
from core.models import User


class Vacation(models.Model):
    class VacationType(models.TextChoices):
        REGULAR = 'regular', 'Regular'
        SICK = 'sick', 'Sick Leave'

    class VacationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        # add revoked deferred and others(?)

    class paymentStatus(models.TextChoices):
        PAID = 'paid', 'Paid'
        UNPAID = 'unpaid', 'Unpaid'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacations')
    start_date = models.DateField()
    end_date = models.DateField()
    vacation_type = models.CharField(max_length=20, choices=VacationType.choices, default=VacationType.REGULAR)
    status = models.CharField(max_length=20, choices=VacationStatus.choices, default=VacationStatus.PENDING)
    

    def __str__(self):
        return f"{self.user.username} - {self.vacation_type} from {self.start_date} to {self.end_date} ({self.status})"
    
    @property
    def phase(self):
        pass
