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
    def build_doctor_shifts(cls, doctor, center):
        """Build the shifts for a doctor."""
        shifts = cls.objects.filter(user=doctor, center=center).all()
        if not shifts:
            return {}
        
        output = {}
        for shift in shifts:
            output[(shift.weekday, shift.index)] = (shift.start_time, shift.end_time)

        return output


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
    def add(cls, doctor, center, week_day, week_index, start_time, end_time):
     
        cls.check_conflicts(doctor, center, week_day, week_index, start_time, end_time)

        new_shift = cls(
            user=doctor,
            center=center,
            weekday=week_day,
            index=week_index,
            start_time=start_time,
            end_time=end_time
        )
        new_shift.save()

        return new_shift

    @staticmethod
    def gen_headers():
        """Generate headers for the table."""
        weekdays = [""] + [x[:3] for x in DIAS_SEMANA] * 5
        indeces = [""] + [((x - 1) // 7) + 1 for x in range(1, 36)]

        header1 = []
        header2 = []
        for i, day in enumerate(weekdays):
            if i == 0:
                header1.append({"cellID": "corner1", "label": ""})
                header2.append({"cellID": "corner2", "label": ""})
                continue

            header1.append({"cellID": f"{(i-1)%7}-{indeces[i]}", "label": day})
            header2.append({"cellID": f"index-{indeces[i]}", "label": indeces[i]})

        return header1, header2
    

class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()
