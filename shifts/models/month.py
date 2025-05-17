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
    

    @classmethod
    def new_month(cls, number, year):
        from core.constants import LEADER

        new_month = cls(year=year, number=number)
        new_month.leader = User.objects.get(crm=LEADER.get('crm'))
        new_month.save()

        return new_month

    def gen_date_row(self):
        end_date = datetime(self.year, self.number, END_DAY)
        if self.number == 1:
            start_date = datetime(self.year - 1, 12, STR_DAY)
        else:
            start_date = datetime(self.year, self.number - 1, STR_DAY)
        
        dates = []
        while start_date <= end_date:
            dates.append(start_date)
            start_date += timedelta(days=1)

        return dates


    def gen_calendar(self):
        pass



class Holiday(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
    day = models.IntegerField()
