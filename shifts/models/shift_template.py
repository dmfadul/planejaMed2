from django.db import models
from shifts.models.shift_abstract import AbstractShift


class TemplateShift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
    weekday = models.IntegerField()
    index = models.IntegerField()
    
    @classmethod
    def add(cls, doctor, center, week_day, week_index, start_time, end_time):   
        new_shift = cls(
            user=doctor,
            center=center,
            weekday=week_day,
            index=week_index,
            start_time=start_time,
            end_time=end_time
        )

        existing_shifts = cls.objects.filter(
            user=doctor,
            weekday=week_day,
            index=week_index,
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
