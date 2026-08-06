from django.db.models import Q
from dataclasses import dataclass
from collections import defaultdict

from core.models import User
from core.constants import DIAS_SEMANA
from vacations.models.vacations import Vacation
from shifts.models import Month, TemplateShift, Shift
from shifts.services.month_services import get_planned_shifts
from dataclasses import replace
from datetime import timedelta


def remove_night_hours(shift):
    """
    Returns the daytime portions of a shift, between 07:00 and 19:00.
    May return zero, one, or two shifts.
    """
    start = shift.start_time
    end = shift.end_time

    # Shift crosses midnight
    if end <= start:
        end += 24

    daytime_parts = []

    # Check the starting day and the following day
    for day_offset in (0, 1):
        daytime_start = day_offset * 24 + 7
        daytime_end = day_offset * 24 + 19

        clipped_start = max(start, daytime_start)
        clipped_end = min(end, daytime_end)

        if clipped_start < clipped_end:
            daytime_parts.append(
                replace(
                    shift,
                    date=shift.date + timedelta(days=day_offset),
                    start_time=clipped_start - day_offset * 24,
                    end_time=clipped_end - day_offset * 24,
                )
            )

    return daytime_parts


def show_vacation_pay_for_month(month: Month):
    vacation_shifts = calculate_vacation_pay_for_month(month)

    shifts_by_user = defaultdict(list)

    for shift in vacation_shifts:
        shifts_by_user[shift.user].append(shift)

    output = ""

    for user, shifts in shifts_by_user.items():
        output += f"{user.name}:\n"

        for shift in shifts:
            weekday = DIAS_SEMANA[shift.date.weekday()]
            start_time = f"{shift.start_time:02d}:00"
            end_time = f"{shift.end_time:02d}:00"

            output += (
                f"{shift.center.abbreviation} - "
                f"Dia {shift.date:%d/%m} - "
                f"{weekday[:3]} - "
                f"{start_time}-{end_time} - "
                f"{(shift.end_time - shift.start_time):02d} horas\n"
            )

        output += "\n"

    return output


def calculate_vacation_pay_for_month(month: Month):
    vacations = Vacation.objects.filter(
        start_date__lte=month.end_date,
        end_date__gte=month.start_date,
        status__in=[
            Vacation.VacationStatus.APPROVED,
            Vacation.VacationStatus.OVERRIDDEN,
        ],
    )

    all_vacation_shifts = []

    for vacation in vacations:
        start_date = max(vacation.start_date, month.start_date.date())
        end_date = min(vacation.end_date, month.end_date.date())

        planned_shifts = get_planned_shifts(
            month,
            user=vacation.user,
        )

        for shift in planned_shifts:
            for daytime_shift in remove_night_hours(shift):
                if not start_date <= daytime_shift.date <= end_date:
                    continue

                if daytime_shift.date.weekday() in (5, 6):
                    continue

                all_vacation_shifts.append(daytime_shift)

    all_vacation_shifts.sort(
        key=lambda shift: (
            shift.user.name.lower(),
            shift.center.abbreviation,
            shift.date,
            shift.start_time,
        )
    )

    return all_vacation_shifts


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
    