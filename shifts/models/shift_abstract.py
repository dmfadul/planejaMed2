from django.db import models
from core.models import User
from core.constants import SHIFTS_MAP


class AbstractShift(models.Model):
    """Class will be inherited by shift and BaseShift."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    end_time = models.IntegerField()

    class Meta:
        abstract = True


    @property
    def hour_list(self) -> list:
        """Returns a list of hours from start to end, wrapping around midnight if needed."""
        return self.gen_hour_list(self.start_time, self.end_time)


    @staticmethod
    def gen_hour_list(start:int, end:int) -> list:
        """Returns a list of hours from start to end, wrapping around midnight if needed."""
        if start == end:
            return [start]
        elif start < end:
            return list(range(start, end))
        else:
            return list(range(start, 24)) + list(range(0, end))


    @staticmethod
    def convert_to_hours(code:str) -> tuple:
        """Convert hour string to tuple of integers."""
        return SHIFTS_MAP.get(code, (0, 0))


    @classmethod
    def convert_to_code(cls, start:int, end:int) -> str:
        # add logic to deal with custom times (that are not in SHIFTS_MAP)
        """Convert start and end time to code."""
        shifts_map = SHIFTS_MAP
        for code, (s, e) in shifts_map.items():
            if s == start and e == end:
                return code
        
        day_range = cls.gen_hour_list(*shifts_map['d'])
        night_range = cls.gen_hour_list(*shifts_map['n'])

        hours = {"day": 0, "night": 0}
        for h in cls.gen_hour_list(start, end):
            if h in day_range:
                hours["day"] += 1
            elif h in night_range:
                hours["night"] += 1
            else:
                continue      
        
        output = ""
        if hours["day"] > 0:
            output += f"d{hours['day']}"
        if hours["night"] > 0:
            output += f"n{hours['night']}"
        
        return output