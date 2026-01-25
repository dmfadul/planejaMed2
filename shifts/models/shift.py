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

    @property
    def date(self):
        return self.gen_date(self.month, self.day)
    
    @transaction.atomic
    def change_user(self, new_user):
        """
        Change the user of this shift. If the new user already has adjacent/overlapping
        shifts on the same center/month/day that can be merged, merge them.
        Transfers user_requests during merge and deletes old shifts.
        Returns None if success; returns a conflicting Shift if there is a hard conflict.
        """
        # Lock this row to avoid concurrent edits during the user change
        Shift.objects.select_for_update().get(pk=self.pk)
        
        # 1) Check for hard conflicts with the new user
        conflict = Shift.check_conflict(
            new_user, self.month, self.day, self.start_time, self.end_time
        )
        if conflict:
            return conflict  # Return the conflicting shift if found
        
        # 2) Reassign the user
        self.user = new_user
        self.save(update_fields=['user'])

        # 3) Find merging candidates (same user, center, month, day)
        candidates = (
            Shift.objects
            .select_for_update()
            .filter(
                user=new_user,
                center=self.center,
                month=self.month,
                day=self.day
            )
            .exclude(pk=self.pk)
            .order_by('start_time', 'end_time')
        )
        
        # iteratively merge with candidates
        base = self
        for other in list(candidates):
            merged = Shift.merge(base, other)
            if merged != -1:
                base = merged

        # 4) invalidate open requests tied to this shift ('base')
        for req in base.user_requests.filter(is_open=True):
            req.invalidate()  # Invalidate all associated user requests

        return None

    @classmethod
    @transaction.atomic
    def merge(cls, shift1, shift2):
        """Merge two shifts, if they complement each other.
        Delete input shifts and returns the merged shift, if merge is possible
        or return -1 if merge is not possible.
        """
        # Lock both rows to avoid concurrent edits during the merge
        Shift.objects.select_for_update().filter(pk__in=[shift1.pk, shift2.pk])

        # Basic compatibility checks
        if not (shift1.user_id == shift2.user_id and
                shift1.center_id == shift2.center_id and
                shift1.month_id == shift2.month_id and
                shift1.day == shift2.day):
            return -1
        
        custom_order = HOUR_RANGE

        hour1 = set(shift1.hour_list)
        hour2 = set(shift2.hour_list)
        merged_hours = sorted(hour1 | hour2, key=lambda x: custom_order.index(x))
        
        # Ensure continuity (no gaps in custom order)
        for i in range(len(merged_hours) - 1):
            if custom_order.index(merged_hours[i]) + 1 != custom_order.index(merged_hours[i + 1]):
                return -1
        
        start_time = merged_hours[0]
        end_time = merged_hours[-1] + 1  # +1 because end_time is exclusive

        # Create the merged shift
        merged = cls.objects.create(
            user=shift1.user,
            center=shift1.center,
            month=shift1.month,
            day=shift1.day,
            start_time=start_time,
            end_time=end_time
        )

        # transfer user requests from both shifts to the merged shift
        shift1.user_requests.update(shift=merged)
        shift2.user_requests.update(shift=merged)

        # Delete the old shifts
        if shift1.pk != merged.pk:
            shift1.delete()
        if shift2.pk != merged.pk:
            shift2.delete()
        
        return merged
    
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
    @transaction.atomic
    def add(cls, doctor, center, month, day, start_time, end_time):
        # Lock all shifts for this doctor/day to avoid races
        existing = (
            cls.objects
            .select_for_update()
            .filter(user=doctor, month=month, day=day)
            .order_by("start_time", "end_time")
        )
    
        # In-memory candidate (no pk yet)
        new_shift = cls(
            user=doctor,
            center=center,
            month=month,
            day=day,
            start_time=start_time,
            end_time=end_time,
        )
    
        # 1) Hard conflict: overlap with a DIFFERENT center
        new_hours = set(new_shift.hour_list)
        for old in existing:
            overlap = not set(old.hour_list).isdisjoint(new_hours)
            if overlap and old.center_id != center.id:
                raise ValueError(
                    f"Conflito - {old.user.name} já tem esse horário no centro {old.center.abbreviation}"
                )
    
        # 2) Save now so reverse-relations are safe if merge() touches them
        new_shift.save()
    
        def touches_or_overlaps(a, b):
            return (
                a.end_time == b.start_time or
                b.end_time == a.start_time or
                not set(a.hour_list).isdisjoint(set(b.hour_list))
            )
    
        # 3) Keep merging with same-center candidates that touch/overlap
        while True:
            candidate = (
                cls.objects
                .select_for_update()
                .filter(user=doctor, month=month, day=day, center=center)
                .exclude(pk=new_shift.pk)
                .order_by("start_time", "end_time")
                .first()
            )
    
            # Find *any* candidate that touches/overlaps (not just overlap)
            merge_target = None
            for s in (
                cls.objects
                .select_for_update()
                .filter(user=doctor, month=month, day=day, center=center)
                .exclude(pk=new_shift.pk)
                .order_by("start_time", "end_time")
            ):
                if touches_or_overlaps(s, new_shift):
                    merge_target = s
                    break
                
            if not merge_target:
                break
            
            merged = cls.merge(merge_target, new_shift)
            if merged == -1:
                break
            new_shift = merged  # merged is saved; old ones deleted inside merge()
    
        return new_shift

    @classmethod
    def gen_date(cls, month, day):
        """Generates the date of the shift as a datetime object."""

        if END_DAY < day <= 31:
            actual_month, actual_year = month.prv_number_year()
        else:
            actual_month, actual_year = month.number, month.year
        return datetime(actual_year, actual_month, day)

    def get_date(self):
        """Returns the date of the shift as a datetime object."""
        return self.gen_date(self.month, self.day)

    def get_overtime_count(self):
        """Returns a dict of overtime and normal hours."""
        actual_date = self.get_date()
        print(actual_date, actual_date.weekday())

        is_holiday = self.day in [h.day for h in self.month.holidays.all()]
        is_weekend = actual_date.weekday() in [5, 6]  # Saturday or Sunday

        if is_holiday or is_weekend:
            return {"normal": 0, "overtime": len(self.hour_list)}
        
        # For weekdays, calculate overtime based on night hours
        day_night_hours = self.get_hours_count()
        return {
            "normal": day_night_hours["day"],
            "overtime": day_night_hours["night"]
        }