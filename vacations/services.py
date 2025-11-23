# services/compliance.py
from dataclasses import dataclass
# from typing import Iterable, List, Tuple, Dict
# from django.db import transaction
# from django.db.models import Exists, OuterRef
# from django.utils import timezone

from core.models import User
from shifts.models import Month, TemplateShift, Shift
# from .models import complianceHistory as ComplianceMonthly


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
    
    users = User.objects.filter(is_active=True, is_invisible=False, is_manager=False) # managers cannot lose eligibility
    for user in users:
        # TODO: exclude users who currently have non-compliant status (they cannot lose what they don't have)
        # TODO: implement a compliant property on User model to simplify this check
        if report_type == "BASE":
            user_delta = get_user_base_total(user, split_the_fifth=True)
            curr_entitlement_months = 10  # TODO: get actual BASE value
        elif report_type == "MONTH":
            user_delta = get_user_month_total(user, month=month)
            curr_entitlement_months = 10  # TODO: get actual MONTH value
        else:
            raise ValueError("Invalid report_type. Must be 'BASE' or 'MONTH'.")
        
        if user_delta.normal < 0 or user_delta.overtime < 0:
            info = {
             "user_id": user.id,
             "user_name": user.name,
             "current_entitlement_months": curr_entitlement_months,
             "reason": user_delta.reason,
            }
            data["items"].append(info)
            data["has_risk"] = True

    data["items"] = sorted(data["items"], key=lambda x: x["user_name"].lower())
    return data
    