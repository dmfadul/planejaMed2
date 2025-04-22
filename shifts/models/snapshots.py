from django.db import models
from core.models import User
from shifts.models.month import Month


class AbstractShiftSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TemplateShiftSnapshot(AbstractShiftSnapshot):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='center_base_snapshots')
    weekday = models.IntegerField()
    index = models.IntegerField()
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='month_base_snapshots')



class ShiftSnapshot(AbstractShiftSnapshot):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='center_shifts_snapshots')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='month_shift_snapshots')
    day = models.IntegerField()
