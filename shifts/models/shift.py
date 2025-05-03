import math
from django.db import models
from core.models import User
from shifts.models.month import Month
from core.constants import SHIFTS_MAP, DIAS_SEMANA


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


    @classmethod
    def check_conflicts(cls, doctor, center, week_day, week_index, start_time, end_time):
        """Check if the shift conflicts with existing shifts."""
        existing_shifts = cls.objects.filter(
            user=doctor,
            weekday=week_day,
            index=week_index,
        ).all()

        print(existing_shifts)
    
    @classmethod
    def add_shift(cls, doctor, center, idx, start_time, end_time):
        week_day = (idx - 1 ) % 7
        week_index = math.ceil(idx / 7)
        
        cls.check_conflicts(doctor, center, week_day, week_index, start_time, end_time)

        new_shift = cls(
            user=doctor,
            center=center,
            weekday=week_day,
            index=week_index,
            start_time=start_time,
        )
        new_shift.save()

        return new_shift

    @staticmethod
    def gen_headers():
        """Generate headers for the table."""
        header1 = [""] + [x[:3] for x in DIAS_SEMANA] * 5
        header2 = [""] + [((x - 1) // 7) + 1 for x in range(1, 36)]
        return header1, header2
    

class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()
