from django.db import models
from shifts.models.shift_abstract import AbstractShift
from core.constants import DIAS_SEMANA, HOUR_RANGE


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


    def get_overtime_count(self, split_the_fifth=True):
        """Returns a dict of overtime and normal hours."""

        if self.weekday in [5, 6]:  # Saturday or Sunday
            normal_hours = 0
            overtime_hours = len(self.hour_list)
            if split_the_fifth and self.index == 5:
                overtime_hours /= 3

            return {"normal": normal_hours, "overtime": overtime_hours}

        # For weekdays, calculate overtime based on night hours
        day_night_hours = self.get_hours_count()
        day_hours = day_night_hours["day"]
        night_hours = day_night_hours["night"]

        if split_the_fifth and self.index == 5:
            day_hours /= 3
            night_hours /= 3

        return {
            "normal": day_hours,
            "overtime": night_hours
        }
        
    @classmethod
    def merge(cls, shift1, shift2):
        """Merge two shifts, if they complement each other.
        Delete input shifts and returns the merged shift, if merge is possible
        or return -1 if merge is not possible.
        """
        custom_order = HOUR_RANGE

        hour_list_1 = shift1.hour_list
        hour_list_2 = shift2.hour_list
        merged_hours = list(set(hour_list_1) | set(hour_list_2))
        merged_hours.sort(key=lambda x: custom_order.index(x))

        # check if the merged hours are continuous
        for i in range(len(merged_hours) - 1):
            if custom_order.index(merged_hours[i]) + 1 != custom_order.index(merged_hours[i + 1]):
                return -1
        
        merged_shift = cls(
            user=shift1.user,
            center=shift1.center,
            weekday=shift1.weekday,
            index=shift1.index,
            start_time=merged_hours[0],
            end_time=merged_hours[-1] + 1 # +1 to include the last hour in the range
        )
        
        return merged_shift