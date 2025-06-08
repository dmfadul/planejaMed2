from django.db import models
from core.models import User
from calendar import monthrange
from datetime import datetime, timedelta
from core.constants import STR_DAY, END_DAY


class Month(models.Model):
    year = models.IntegerField()
    number = models.IntegerField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='month_leader')
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.year}-{self.number}"
    
    @property
    def start_date(self):
        if self.number == 1:
            start_date = datetime(self.year - 1, 12, STR_DAY)
        else:
            start_date = datetime(self.year, self.number - 1, STR_DAY)
        return start_date
    
    @property
    def end_date(self):
        return datetime(self.year, self.number, END_DAY)
    
    @property
    def break_date(self):
        _, last_day = monthrange(self.start_date.year, self.start_date.month)
        return datetime(self.start_date.year, self.start_date.month, last_day)

    @classmethod
    def new_month(cls, number, year):
        from core.constants import LEADER

        new_month = cls(year=year, number=number)
        new_month.leader = User.objects.get(crm=LEADER.get('crm'))
        new_month.save()

        return new_month
    
    @classmethod
    def get_current(cls):
        current_month = cls.objects.filter(is_current=True).first()
        
        return current_month if current_month else None
    
    def populate_month(self):
        from . import Shift, TemplateShift
        
        print(f"Populating month {self}...")

        year, month = self.year, self.number
        first_day = datetime(year, month, 1)
        first_wday = first_day.weekday()  # Monday is 0

        prv_year, prv_month = self.start_date.year, self.start_date.month
        prv_first_day = datetime(prv_year, prv_month, 1)
        prv_first_wday = prv_first_day.weekday()  # Monday is 0

        templates = TemplateShift.objects.filter(user__is_active=True)

        for t in templates:
            day_offset_curr = (t.weekday - first_wday + 7) % 7
            day_offset_prv = (t.weekday - prv_first_wday + 7) % 7

            first_ocurrence_curr = first_day + timedelta(days=day_offset_curr)
            first_ocurrence_prv = prv_first_day + timedelta(days=day_offset_prv)


            target_date_curr = first_ocurrence_curr + timedelta(weeks=t.index-1)
            target_date_prv = first_ocurrence_prv + timedelta(weeks=t.index-1)

            if self.start_date <= target_date_curr <= self.end_date:
                new_shift = Shift.objects.create(
                    user=t.user,
                    center=t.center,
                    month=self,
                    day=target_date_curr.day,
                    start_time=t.start_time,
                    end_time=t.end_time
                )
            
            if self.start_date <= target_date_prv <= self.end_date:
                new_shift = Shift.objects.create(
                    user=t.user,
                    center=t.center,
                    month=self,
                    day=target_date_prv.day,
                    start_time=t.start_time,
                    end_time=t.end_time
                )

        print(f"Month {self} populated.")

    def gen_date_row(self):
        start_date = self.start_date
        end_date = self.end_date
        
        dates = []
        while start_date <= end_date:
            dates.append(start_date)
            start_date += timedelta(days=1)

        return dates

    def gen_calendar_table(self):
        cal_table = []
        week = [""] * 7
        current_date = self.start_date

        while current_date <= self.end_date:
            weekday = current_date.weekday()
            week[weekday] = current_date.day
            if weekday == 6:  # Sunday
                cal_table.append(week)
                week = [""] * 7
            current_date += timedelta(days=1)
        if any(week):
            cal_table.append(week)
        return cal_table




class Holiday(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
    day = models.IntegerField()
