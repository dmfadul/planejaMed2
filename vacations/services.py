# services/compliance.py
from django.db.models import Q
from dataclasses import dataclass
# from typing import Iterable, List, Tuple, Dict
# from django.db import transaction
# from django.db.models import Exists, OuterRef
# from django.utils import timezone

from core.models import User
from core.constants import DIAS_SEMANA
from vacations.models.vacations import Vacation
from shifts.models import Month, TemplateShift, Shift

# from .models import complianceHistory as ComplianceMonthly


def calculate_vacation_pay_for_month(month: Month):
    vacations = Vacation.objects.filter(
        start_date__lte=month.end_date,
        end_date__gte=month.start_date,
        status__in=[
            Vacation.VacationStatus.APPROVED,
            Vacation.VacationStatus.OVERRIDDEN,
        ]
    )
        
    output = ""
    for vacation in vacations:
        str_day = max(vacation.start_date, month.start_date.date()).day
        end_day = min(vacation.end_date, month.end_date.date()).day
        output += f"{vacation.user.name}:\n"
        
        if str_day <= end_day:
            shifts = Shift.objects.filter(
                month=month,
                user=vacation.user,
                day__range=(str_day, end_day),
            )
        else:
            shifts = Shift.objects.filter(
                month=month,
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


@dataclass
class TotalBaseHours:
    normal: float
    overtime: float

    def __sub__(self, other):
        if isinstance(other, dict):
            if (not "normal" in other) or (not "overtime" in other):
                raise ValueError("Dict must have 'normal' and 'overtime' keys.")
            n = other.get("normal", 0)
            o = other.get("overtime", 0)
        elif isinstance(other, TotalBaseHours):
            n = other.normal
            o = other.overtime
        else:
            return NotImplemented
        
        return TotalBaseHours(
            normal=self.normal - n,
            overtime=self.overtime - o
        )
    
    def __isub__(self, other):
        if isinstance(other, dict):
            if (not "normal" in other) or (not "overtime" in other):
                raise ValueError("Dict must have 'normal' and 'overtime' keys.")
            n = other.get("normal", 0)
            o = other.get("overtime", 0)
        elif isinstance(other, TotalBaseHours):
            n = other.normal
            o = other.overtime
        else:
            return NotImplemented
        
        self.normal -= n
        self.overtime -= o
        return self
    
    @property
    def reason(self):
        if self.normal >= 0 and self.overtime >= 0:
            return "Sufficient normal and overtime hours."
        reason = ""
        if self.normal < 0:
            reason += f"Rotina: está faltando {abs(self.normal)} horas.\n"
        if self.overtime < 0:
            reason += f"Plantão: está faltando {abs(self.overtime)} horas.\n"
        return reason


def get_user_base_total(user, split_the_fifth=False):
    """
    compute the total base hours for a user, considering split_the_fifth flag.
    To be run when new month is created (base is 'set in place').
    """
    from core.constants import VACATION_RULES

    vac_rules = VACATION_RULES
    total = TotalBaseHours(normal=0, overtime=0)

    base_shifts = TemplateShift.objects.filter(user=user)
    for shift in base_shifts:
        normal_hours = shift.get_overtime_count()["normal"]
        overtime_hours = shift.get_overtime_count()["overtime"]
        
        if split_the_fifth and shift.index == 5:  # Fifth week
            # Split hours into thirds because fifth week occurs 1/3 of the time
            normal_hours /= 3
            overtime_hours /= 3

        total.normal += normal_hours
        total.overtime += overtime_hours

    if user.date_joined <= vac_rules.get("new_policy_start_date"):
        user_rules = vac_rules.get("old_policy_hours")
    else:
        user_rules = vac_rules.get("new_policy_hours")

    user_delta = total - user_rules
    return user_delta


def get_user_month_total(user, month: Month):
    """
    compute the total hours in a month for a user, does not need split_the_fifth flag,
    because it is only called when the month is already determined, so the number of weeks
    is known.
    To be run when new month is opened (shifts exchanges are closed).
    """
    from core.constants import VACATION_RULES

    vac_rules = VACATION_RULES
    total = TotalBaseHours(normal=0, overtime=0)

    shifts = Shift.objects.filter(user=user)
    for shift in shifts:        
        total.normal += shift.get_overtime_count()["normal"]
        total.overtime += shift.get_overtime_count()["overtime"]

    if user.date_joined <= vac_rules.get("new_policy_start_date"):
        user_rules = vac_rules.get("old_policy_hours")
    else:
        user_rules = vac_rules.get("new_policy_hours")

    user_delta = total - user_rules
    return user_delta


def gen_compliance_report(month: Month, report_type: str, exclude_noncompliant=False):
    """
    Generate a report of users at risk of losing vacation eligibility for changes on the base schedule.
    """

    data = {
        "year": month.year,
        "month": month.number,
        "has_risk": False,
        "items": []
    }
    
    users = User.objects.filter(
        is_active=True,
        is_invisible=False,
        is_manager=False,                   # managers cannot lose eligibility
    )

    for user in users:
        if user.compliant_since is None and exclude_noncompliant:
            continue
        if report_type == "BASE":
            user_delta = get_user_base_total(user, split_the_fifth=True)
        elif report_type == "MONTH":
            user_delta = get_user_month_total(user, month=month)
        else:
            raise ValueError("Invalid report_type. Must be 'BASE' or 'MONTH'.")
        
        if user_delta.normal < 0 or user_delta.overtime < 0:
            info = {
             "user_id": user.id,
             "user_name": user.name,
             "current_entitlement_months": user.months_compliant_count,
             "reason": user_delta.reason,
            }
            data["items"].append(info)
            data["has_risk"] = True

    data["items"] = sorted(data["items"], key=lambda x: x["user_name"].lower())
    return data
    