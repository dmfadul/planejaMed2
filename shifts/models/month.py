from django.db import models
from core.models import User
from calendar import monthrange
from datetime import datetime, timedelta
from shifts.utils.calendar_utils import gen_date_row, gen_calendar_table
from shifts.services.month_services import populate_month as _populate_month
from core.constants import STR_DAY, END_DAY, MESES


class MonthManager(models.Manager):
    def current(self):
        return self.filter(is_current=True).first()
    
    def next(self):
        return self.filter(is_locked=True).first()


class Month(models.Model):
    year = models.IntegerField()
    number = models.IntegerField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='month_leader')
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='months', blank=True)

    objects = MonthManager()

    def __str__(self):
        return f"{self.year}-{self.number}"
    
    # ---- Properties ----
    @property
    def name(self):
        return MESES[self.number - 1]
    
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
    
    @property
    def size(self):
        return (self.end_date - self.start_date).days + 1

    # ---- Class Methods ----

    @classmethod
    def new_month(cls, number, year):
        from core.constants import LEADER
        check = cls.objects.filter(year=year, number=number).first()
        if check:
            raise ValueError(f"Month {year}-{number} already exists.")

        new_month = cls(year=year, number=number)
        new_month.leader = User.objects.get(crm=LEADER.get('crm'))
        new_month.save()

        return new_month
    
    @classmethod
    def get_current(cls):
        current_month = cls.objects.filter(is_current=True).first()
        
        return current_month if current_month else None
    
    

    def get_previous(self):
        if self.number == 1:
            prv_month, prv_year = 12, self.year - 1
        else:
            prv_month, prv_year = self.number - 1, self.year
        
        return Month.objects.filter(year=prv_year, number=prv_month).first()
    

    # ---- Instance Methods ----
    def toggle_holiday(self, day):
        if not (1 <= day <= 31):
            raise ValueError("Day must be between 1 and 31.")
        
        if day in self.holidays.all():
            return
        
        new_holiday = Holiday(month=self, day=day)
        new_holiday.save()
        
        return True

    def next_number_year(self):
        if self.number == 12:
            return 1, self.year + 1
        else:
            return self.number + 1, self.year
        
    def prv_number_year(self):
        if self.number == 1:
            return 12, self.year - 1
        else:
            return self.number - 1, self.year
        
    def fix_users(self):
        active_users = User.objects.filter(is_active=True, is_invisible=False)
        self.users.set(active_users)

    def include_user(self, user):
        if not isinstance(user, User):
            raise ValueError("Expected a User instance.")
        self.users.add(user)

    def exclude_user(self, user):
        if not isinstance(user, User):
            raise ValueError("Expected a User instance.")
        self.users.remove(user)

    def populate_month(self):
        _populate_month(self)

    def gen_date_row(self):
        return gen_date_row(self.start_date, self.end_date)

    def gen_calendar_table(self):
        return gen_calendar_table(self.start_date, self.end_date)




class Holiday(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
    day = models.IntegerField()
