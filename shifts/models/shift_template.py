from django.db import models
from core.constants import SHIFTS_MAP, DIAS_SEMANA
from shifts.models.shift_abstract import AbstractShift


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
    def check_conflicts(cls, test_shift):
        """Check if the shift conflicts with existing shifts."""
        existing_shifts = cls.objects.filter(
            user=test_shift.user,
            weekday=test_shift.weekday,
            index=test_shift.index,
        ).all()

        same_center_shifts = existing_shifts.filter(center=test_shift.center)
        other_centers_shifts = existing_shifts.exclude(center=test_shift.center)
        
        for shift in other_centers_shifts:
            if not set(shift.hour_list).isdisjoint(test_shift.hour_list):
                raise ValueError(
                    f"Conflito - {shift.user.name} já tem esse horário na base {shift.center.abbreviation}"
                )
        
        for shift in same_center_shifts:
            if not set(shift.hour_list).isdisjoint(test_shift.hour_list):
                # merge shifts if needed
                return 0


    
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

        cls.check_conflicts(new_shift)

        # new_shift.save()

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