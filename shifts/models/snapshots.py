from django.db import models
from core.models import User
from shifts.models import Month, Center


class ShiftType(models.TextChoices):
    BASE = 'base', 'Base'
    ORIGINAL = 'original', 'Original'
    REALIZED = 'realized', 'Realized'


class ShiftSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='shiftsnapshots')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shiftsnapshots')
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    weekday = models.IntegerField(null=True, blank=True)
    index = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=10, choices=ShiftType.choices)

    class Meta:
        indexes = [
            models.Index(fields=['center', 'month', 'type']),
        ]
    