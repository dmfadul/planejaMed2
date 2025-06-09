from django.db import models
from shifts.models.shift_abstract import AbstractShift
from core.constants import DIAS_SEMANA


class TemplateShift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
    weekday = models.IntegerField()
    index = models.IntegerField()

    def __str__(self):
        day = f"{DIAS_SEMANA[self.weekday]}({self.index})"
        return f"{self.center.abbreviation} - {self.user.abbr_name} - {day} - {self.start_time} to {self.end_time}"
    
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

        for old_shift in existing_shifts:
            shifts_overlap = not set(old_shift.hour_list).isdisjoint(set(new_shift.hour_list))
            if shifts_overlap and not old_shift.center == new_shift.center:
                raise ValueError(
                    f"Conflito - {old_shift.user.name} já tem esse horário no centro {old_shift.center.abbreviation}"
                )
            
            if old_shift.center == new_shift.center:
                merged_shift = cls.merge(old_shift, new_shift)
                if merged_shift != -1:
                    # If the merge was successful, delete the old shift
                    old_shift.delete()
                    new_shift = merged_shift
        
        new_shift.save()          
        return new_shift


    def get_overtime_count(self):
        """Returns a dict of overtime and normal hours."""

        if self.weekday in [5, 6]:  # Saturday or Sunday
            return {"normal": 0, "overtime": len(self.hour_list)}
        
        # For weekdays, calculate overtime based on night hours
        day_night_hours = self.get_hours_count()
        return {
            "normal": day_night_hours["day"],
            "overtime": day_night_hours["night"]
        }
        
        
        
        
        
        
        
        
        