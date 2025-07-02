from django.db import models
from datetime import datetime
from shifts.models.month import Month
from core.constants import STR_DAY, END_DAY
from shifts.models.shift_abstract import AbstractShift
  
  
class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()

    def __str__(self):
        return f"{self.center.abbreviation} - {self.user.abbr_name} - {self.month.number}/{self.day} - {self.start_time} to {self.end_time}"

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

        for old_shift in existing_shifts:
            shifts_overlap = not set(old_shift.hour_list).isdisjoint(set(new_shift.hour_list))
            if shifts_overlap and not old_shift.center == new_shift.center:
                raise ValueError(
                    f"Conflito - {old_shift.user.name} já tem esse horário no centro {old_shift.center.abbreviation}"
                )

            if old_shift.center == new_shift.center:
                # Attempt to merge the shifts
                merged_shift = cls.merge(old_shift, new_shift)
                if merged_shift != -1:
                    # If the merge was successful, delete the old shift
                    old_shift.delete()
                    new_shift = merged_shift
        
        new_shift.save()
        return new_shift


    def get_date(self):
        """Returns the date of the shift as a datetime object."""

        if END_DAY <= self.day <= 31:
            actual_month, actual_year = self.month.prv_number_year()
        else:
            actual_month, actual_year = self.month.number, self.month.year
        return datetime(actual_year, actual_month, self.day)

    def get_overtime_count(self):
        """Returns a dict of overtime and normal hours."""
        actual_date = self.get_date()

        is_holiday = self.day in [h.day for h in self.month.holidays.all()]
        is_weekend = actual_date.weekday in [5, 6]  # Saturday or Sunday

        if is_holiday or is_weekend:
            return {"normal": 0, "overtime": len(self.hour_list)}
        
        # For weekdays, calculate overtime based on night hours
        day_night_hours = self.get_hours_count()
        return {
            "normal": day_night_hours["day"],
            "overtime": day_night_hours["night"]
        }