from django.db import models
from core.models import User
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

    @classmethod
    def new_month(cls, number, year):
        from core.constants import LEADER

        new_month = cls(year=year, number=number)
        new_month.leader = User.objects.get(crm=LEADER.get('crm'))
        new_month.save()

        return new_month

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
