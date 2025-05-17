from django.db import models
from shifts.models.month import Month
from shifts.models.shift_abstract import AbstractShift
  
  
class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()


    @classmethod
    def add(cls, doctor, center, month, day, start_time, end_time):
        new_shift = cls(
            user=doctor,
            center=center,
            month=month,
            day=day,
            start_time=start_time,
            end_time=end_time
        )

        existing_shifts = cls.objects.filter(
            user=doctor,
            month=month,
            day=day,
        ).all()

        for shift in existing_shifts:
            if not set(shift.hour_list).isdisjoint(new_shift.hour_list):
                raise ValueError(
                    f"Conflito - {shift.user.name} já tem esse horário na base {shift.center.abbreviation}"
                )

            if shift.center == new_shift.center:
                new_shift.merge(shift)
        
        new_shift.save()
        return new_shift
