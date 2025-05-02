from django.db import models
from core.models import User
from shifts.models.month import Month
from core.constants import SHIFTS_MAP


class AbstractShift(models.Model):
    """Class will be inherited by shift and BaseShift."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    end_time = models.IntegerField()

    class Meta:
        abstract = True

    @staticmethod
    def convert_to_time(code:str) -> tuple:
        """Convert hour string to tuple of integers."""
        
        print(SHIFTS_MAP)
        return 1, 2


class TemplateShift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
    weekday = models.IntegerField()
    index = models.IntegerField()


class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()
