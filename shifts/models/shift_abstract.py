from django.db import models
from core.models import User
from core.constants import SHIFTS_MAP, HOUR_RANGE, MORNING_START


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
        if start == end and start != MORNING_START:
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
        if hours["day"]:
            output += "d" if hours["day"] == 12 else f"d{hours['day']}"
        if hours["night"]:
            output += "n" if hours["night"] == 12 else f"n{hours['night']}"
        
        return output
    

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
    

    def get_hours_count(self):
        shifts_map = SHIFTS_MAP
        day_range = self.gen_hour_list(*shifts_map['d'])
        night_range = self.gen_hour_list(*shifts_map['n'])

        hours_count = {"day": 0, "night": 0}
        for hour in self.hour_list:
            if hour in day_range:
                hours_count["day"] += 1
            elif hour in night_range:
                hours_count["night"] += 1

        print(self.hour_list, self.weekday, self.index, self.user, self.start_time, self.end_time)
        return hours_count