from django.db import models
from core.models import User
from shifts.models.month import Month


class AbstractShift(models.Model):
    """Class will be inherited by shift and BaseShift."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        abstract = True


class TemplateShift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
    weekday = models.IntegerField()
    index = models.IntegerField()


class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()


class ShiftSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shift_snapshots')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shift_snapshots')
    day = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['snapshot_month']),
        ]
