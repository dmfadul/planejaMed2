from django.db import models
from core.models import User
from core.constants import SHIFTS_MAP, SHIFT_CODES, MORNING_START


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
    def format_hours(cls, start:int, end:int) -> list:
        """Split and format hours into a redundant list of string representations."""
        shifts_map = SHIFTS_MAP

        output = {}
        for hour in cls.gen_hour_list(start, end):
            for code in shifts_map.keys():
                if code not in output:
                    output[code] = []
                if hour in cls.gen_hour_list(*shifts_map[code]):
                    output[code].append(hour)

        if not output:
            return []

        formatted_hours = []
        for code, hours in output.items():
            if not hours:
                continue
            
            start, end = hours[0], hours[-1] + 1  # +1 to include the last hour in the range
            formatted_hours.append(f"{code}: {start:02d}:00 - {end:02d}:00")

        code_order = SHIFT_CODES
        order_map = {val: idx for idx, val in enumerate(code_order)}
        formatted_hours.sort(key=lambda x: order_map.get(x, len(code_order)))
        return formatted_hours

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
    def stringfy_codes(cls, codes:list) -> str:
        """Convert a list of codes to a string."""
        if not codes:
            return ""
        
        code_order = SHIFT_CODES
        order_map = {val: idx for idx, val in enumerate(code_order)}
        codes.sort(key=lambda x: order_map.get(x, len(code_order)))
        code = "".join(codes)

        return code
        

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

        return hours_count

    @classmethod
    def merge(cls):
        raise NotImplementedError("This method should be implemented in subclasses.")