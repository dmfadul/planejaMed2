from django.db import models
from core.constants import SHIFTS_MAP, DIAS_SEMANA
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