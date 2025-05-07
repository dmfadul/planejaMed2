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
    
    def merge(self, new_shift):
        """Merge two shifts, if they overlap."""

        print("tehy not the same1", self.hour_list, new_shift.hour_list)

        # check if the shifts are the same
        if self.start_time == new_shift.start_time and self.end_time == new_shift.end_time:
            print("they the same", self.hour_list, new_shift.hour_list)
            # new_shift.delete()
            return self
        
        print("tehy not the same", self.hour_list, new_shift.hour_list)
        
        # # check if the shifts are adjacent (old -> new)
        # if self.end_time == new_shift.start_time:
        #     self.end_time = new_shift.end_time
        #     self.save()
        #     new_shift.delete()
        #     return self
        
        # # check if the shifts are adjacent (new -> old)
        # if new_shift.end_time == self.start_time:
        #     self.start_time = new_shift.start_time
        #     self.save()
        #     new_shift.delete()
        #     return self

        # # check if the shifts are disjoint
        # if set(self.hour_list).isdisjoint(new_shift.hour_list):
        #     return -1
        
        # # check if new_shift is inside old_shift
        # if new_shift.start_time in self.hour_list and (new_shift.end_time in self.hour_list or new_shift.end_time == self.end_time):
        #     new_shift.delete()
        #     return self
        
        # # check if old_shift is inside new_shift
        # if self.start_time in new_shift.hour_list and (self.end_time in new_shift.hour_list or self.end_time == new_shift.end_time):
        #     self.start_time = new_shift.start_time
        #     self.end_time = new_shift.end_time
        #     self.save()
        #     new_shift.delete()
        #     return self
        
        # # check if new_shift overlaps old_shift (old -> new)
        # if new_shift.start_time in self.hour_list or new_shift.start_time == self.end_time:
        #     self.end_time = new_shift.end_time
        #     self.save()
        #     new_shift.delete()
        #     return self
        
        # # check if old_shift overlaps new_shift (new -> old)
        # if new_shift.end_time in self.hour_list:
        #     self.start_time = new_shift.start_time
        #     self.save()
        #     new_shift.delete()
        #     return self

        # self.save()
        # return self