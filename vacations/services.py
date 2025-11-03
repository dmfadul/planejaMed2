# services/compliance.py
from dataclasses import dataclass
from typing import Iterable, List, Tuple, Dict
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone

from core.models import User
from shifts.models import Month, TemplateShift, Shift  # adjust imports
from .models import complianceHistory as ComplianceMonthly


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
        
        if split_the_fifth and shift.weekday in [5, 6]:  # Saturday or Sunday
            # Split normal hours into half normal and half overtime
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


def gen_base_compliance_report(month: Month = None):
    """
    Generate a report of users at risk of losing vacation eligibility for changes on the base schedule.
    """

    data = {
        "year": month.year if month else timezone.now().year,
        "month": month.number if month else timezone.now().month,
        "has_risk": False,
        "items": []
    }
    
    users = User.objects.filter(is_active=True, is_invisible=False, is_manager=False) # managers cannot lose eligibility
    for user in users:
        user_delta = get_user_base_total(user, split_the_fifth=True)
        if user_delta.normal < 0 or user_delta.overtime < 0:
            info = {
             "user_id": user.id,
             "user_name": user.name,
             "current_entitlement_months": 10, # TODO: get actual value
             "reason": user_delta.reason,
            }
            data["items"].append(info)
            data["has_risk"] = True

    data["items"] = sorted(data["items"], key=lambda x: x["user_name"].lower())
    return data
    

def get_user_month_total(user, split_the_fifth=False):
    """
    compute the total hours in a month for a user, considering split_the_fifth flag.
    To be run when new month is opened (shifts exchanges are closed).
    """
    # does it need split the fifth?
    # probably needs month as argument
    pass

def gen_month_compliance_report(month: Month = None):
    """
    Generate a report of users at risk of losing vacation eligibility for changes on the base schedule.
    """
    pass