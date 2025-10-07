from django.db import models, transaction
from datetime import datetime
from shifts.models.month import Month
from core.constants import STR_DAY, END_DAY, HOUR_RANGE
from shifts.models.shift_abstract import AbstractShift
  
  
class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()

    def __str__(self):
        return f"{self.center.abbreviation} - {self.user.abbr_name} - {self.month.number}/{self.day} - {self.start_time} to {self.end_time}"

    def change_user(self, new_user):
        # check for conflicts before changing user
        # TODO: merge with existing shifts for new_user if needed
        conflict = Shift.check_conflict(new_user,
                                        self.month,
                                        self.day,
                                        self.start_time,
                                        self.end_time)
        
        if conflict:
            return conflict  # Return the conflicting shift if found
        
        self.user = new_user
        self.save(update_fields=['user'])

        merging_shifts = Shift.objects.filter(
            user=new_user,
            month=self.month,
            day=self.day,
        ).exclude(pk=self.pk).all()

        for other in merging_shifts:
            merged = Shift.merge(self, other)
            if merged != -1:
                # other.delete()
                print(other)
                self = merged  # Update self to the merged shift

        for req in self.user_requests.filter(is_open=True):
            req.invalidate()  # Invalidate all associated user requests

        return None  # No conflict, user changed successfully

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
            month=shift1.month,
            day=shift1.day,
            start_time=merged_hours[0],
            end_time=merged_hours[-1] + 1 # +1 to include the last hour in the range
        )
        
        return merged_shift
    
    @transaction.atomic
    def split(self, split_start, split_end):
        """
        Split the current shift into:
          • two parts if one split boundary coincides with current start or end; or
          • three parts if both split boundaries are strictly inside.
        Returns the 'middle' segment [split_start, split_end) as a new Shift when a split occurs.
        Returns self if the split covers the whole shift (i.e., no split needed).
        Returns None for invalid splits.
        """

        # Lock this row to avoid concurrent edits during the split
        Shift.objects.select_for_update().get(pk=self.pk)
        
        original_hours = set(self.hour_list)

        # must be aligned to existing discrete hours (inclusive start, exclusive end)
        if not (split_start in original_hours and (split_end-1) in original_hours):
            return None
        
        # No split needed: requested middle covers entire shift
        if split_start == self.start_time and split_end == self.end_time:
            return self
        
        third_shift = None
        # === Case A: split into three parts (both strictly inside)
        if not (split_start == self.start_time) and not (split_end == self.end_time):            
            third_shift = Shift.objects.create(
                user=self.user,
                center=self.center,
                month=self.month,
                day=self.day,
                start_time=split_end,
                end_time=self.end_time
            )

            # adjust the current shift to be the start part
            self.end_time = split_start
            self.save(update_fields=['end_time'])

            # create the middle part
            new_shift = Shift.objects.create(
                user=self.user,
                center=self.center,
                month=self.month,
                day=self.day,
                start_time=split_start,
                end_time=split_end
            )

        # === Case B: split into two parts at the left edge
        elif split_start == self.start_time:
            # adjust the current shift to be the end part
            self.start_time = split_end
            self.save(update_fields=['start_time'])

            # new middle becomes the left-edge chunk
            new_shift = Shift.objects.create(
                user=self.user,
                center=self.center,
                month=self.month,
                day=self.day,
                start_time=split_start,
                end_time=split_end,
            )
        # === Case C: split into two parts at the right edge
        elif split_end == self.end_time:
            # turn current into the left part
            self.end_time = split_start
            self.save(update_fields=['end_time'])

            # new middle becomes the right-edge chunk
            new_shift = Shift.objects.create(
                user=self.user,
                center=self.center,
                month=self.month,
                day=self.day,
                start_time=split_start,
                end_time=split_end,
            )
        else:
            return None  # Should not reach here

        # --- Reassign or invalidate open requests ---
        # Build hour sets for membership checks to avoid confusion after mutations.
        old_hours = set(range(self.start_time, self.end_time))
        new_hours = set(range(new_shift.start_time, new_shift.end_time))
        third_hours = set(range(third_shift.start_time, third_shift.end_time)) if third_shift else set()

        # We treat a request as "fits" if its [start_hour, end_hour) is fully contained.
        for r in self.user_requests.filter(is_open=True).select_for_update():
            req_hours = set(range(r.start_hour, r.end_hour))

            if req_hours.issubset(new_hours):
                r.shift = new_shift
                r.save(update_fields=['shift'])
                continue

            if third_shift and req_hours.issubset(third_hours):
                r.shift = third_shift
                r.save(update_fields=['shift'])
                continue

            if req_hours.issubset(old_hours):
                # still fits current (left) part; no reassignment needed
                continue

            # otherwise, it no longer fits any segment -> invalidate
            r.invalidate()
            
        return new_shift


    @classmethod
    def check_conflict(cls, doctor, month, day, start_time, end_time):
        """Check if a new shift conflicts with existing shifts for the same doctor."""
        new_shift_hours = cls.gen_hour_list(start_time, end_time)

        existing_shifts = cls.objects.filter(
            user=doctor,
            month=month,
            day=day,
        ).all()

        for old_shift in existing_shifts:
            if not set(old_shift.hour_list).isdisjoint(set(new_shift_hours)):
                return old_shift  # Conflict found

        return None  # No conflict

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