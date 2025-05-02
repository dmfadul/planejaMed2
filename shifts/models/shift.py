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
    def convert_to_hours(code:str) -> tuple:
        """Convert hour string to tuple of integers."""
        return SHIFTS_MAP.get(code, (0, 0))

    @staticmethod
    def convert_to_code(start:int, end:int) -> str:
        # add logic to deal with custom times (that are not in SHIFTS_MAP)
        """Convert start and end time to code."""
        for code, (s, e) in SHIFTS_MAP.items():
            if s == start and e == end:
                return code
        return -1


class TemplateShift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
    weekday = models.IntegerField()
    index = models.IntegerField()


class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()
