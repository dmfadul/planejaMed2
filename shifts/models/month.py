from django.db import models
from core.models import User
from calendar import monthrange
from datetime import datetime, timedelta
from shifts.utils.calendar_utils import gen_date_row, gen_calendar_table
from shifts.services.month_services import populate_month as _populate_month
from core.constants import STR_DAY, END_DAY, MESES, DIAS_SEMANA
from django.db.models import Q


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
    def days(self):
        '''Generate a list of all days (in date format) in the month period.'''
        
        days_list = []
        current_day = self.start_date
        while current_day <= self.end_date:
            days_list.append(current_day)
            current_day += timedelta(days=1)
        return days_list

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
        
        if day in [h.day for h in self.holidays.all()]:
            # If the holiday already exists, remove it
            self.holidays.filter(day=day).delete()
            return True
        
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

    def unlock(self):
        from . import ShiftSnapshot, ShiftType

        previous = self.get_previous()
        if previous:
            previous.is_current = False
            previous.save()

        self.is_locked = False
        self.is_current = True
        self.save()

        ShiftSnapshot.take_snapshot(self, ShiftType.ORIGINAL)

    def calculate_vacation_pay(self):
        from vacations.models.vacations import Vacation
        from shifts.models import Shift

        vacations = Vacation.objects.filter(
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            status__in=[
                Vacation.VacationStatus.APPROVED,
                Vacation.VacationStatus.OVERRIDDEN,
            ]
        )
            
        output = ""
        for vacation in vacations:
            str_day = max(vacation.start_date, self.start_date.date()).day
            end_day = min(vacation.end_date, self.end_date.date()).day
            output += f"{vacation.user.name}:\n"
            
            if str_day <= end_day:
                shifts = Shift.objects.filter(
                    month=self,
                    user=vacation.user,
                    day__range=(str_day, end_day),
                )
            else:
                shifts = Shift.objects.filter(
                    month=self,
                    user=vacation.user,
                ).filter(
                    Q(day__gte=str_day) | Q(day__lte=end_day)
                )

            shifts = shifts.order_by("center__name")
                   
            for s in shifts:
                s_month = f"{s.month.number:02d}"
                s_weekday = DIAS_SEMANA[s.date.weekday()]
                s_str_time = f"{s.start_time:02d}:00"
                s_end_time = f"{s.end_time:02d}:00"
                
                output += f"""Dia {s.day}/{s_month} - {s_weekday}- {s_str_time}-{s_end_time} - {s.center.abbreviation} \n"""
            output += "\n"

        return output


class Holiday(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
    day = models.IntegerField()

    class Meta:
        unique_together = ('month', 'day')  # Ensures (month, day) is unique