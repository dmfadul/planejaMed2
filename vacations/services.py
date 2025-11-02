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
    # TODO: exclude users who currently have non-compliant status (they cannot lose what they don't have)
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

@dataclass
class ComplianceEval:
    user_id: int
    month_id: int
    status: str                 # "C" | "N" | "U"
    reason: Dict                # JSON-safe dict
    will_lose_privileges: bool  # eligibility drops when this month is considered

# --- A) PURE EVALUATION ---

def rules_pass_for_base(user: User, month: Month):
    """
    Placeholder for the actual rules engine logic.
    Should return an object with .ok (bool), .details (dict), .summary (str).
    """
    # Implement your actual rules here.
    class Result:
        def __init__(self, ok, details, summary):
            self.ok = ok
            self.details = details
            self.summary = summary

    # Example logic (to be replaced):
    ok = True  # or False based on rules
    details = {"example_rule": {"required": 5, "actual": 5, "pass": True}}
    summary = "All rules passed." if ok else "Some rules failed."

    return Result(ok, details, summary)

def evaluate_user_month(user: User, month: Month) -> Tuple[str, Dict]:
    """
    Return (status, reason) for a single user+month WITHOUT writing to DB.
    """
    passed = rules_pass_for_base(user=user, month=month)  # <- your function(s)
    reason = {
        "ruleset": "vac-eligibility",
        "details": passed.details,  # e.g. dict of per-rule {required, actual, pass}
        "summary": passed.summary,
    }
    return (ComplianceMonthly.ComplianceStatus.COMPLIANT if passed.ok else ComplianceMonthly.ComplianceStatus.NONCOMPLIANT, reason)


def eligible_last_6(user: User, end_month: Month) -> bool:
    """Derive eligibility from history: need C in the 6-month window ending at end_month."""
    window = (Month.objects
              .filter(start_date__lte=end_month.start_date)
              .order_by("-start_date")
              [:6])
    if len(window) < 6:
        return False
    window_ids = [m.id for m in window]
    got = ComplianceMonthly.objects.filter(user=user, month_id__in=window_ids)\
                                   .values_list("month_id", "status")
    by_mid = dict(got)
    return all(by_mid.get(mid) == ComplianceMonthly.ComplianceStatus.COMPLIANT for mid in window_ids)


def preview_month(month: Month, users: Iterable[User] = None) -> List[ComplianceEval]:
    """
    Compute what we WOULD store for `month`, and who would lose eligibility
    (eligible up to previous month, not eligible after including `month`).
    """
    users = list(users) if users is not None else list(User.objects.filter(is_active=True, is_invisible=False))

    # previous complete month (for prior eligibility)
    month_before = (Month.objects.filter(start_date__lt=month.start_date)
                               .order_by("-start_date").first())

    out: List[ComplianceEval] = []
    for u in users:
        status, reason = evaluate_user_month(u, month)

        was_eligible = eligible_last_6(u, month_before) if month_before else False
        # Pretend this month's record exists with `status`:
        now_eligible = _eligible_after_including(u, month, status)

        out.append(ComplianceEval(
            user_id=u.id,
            month_id=month.id,
            status=status,
            reason=reason,
            will_lose_privileges=(was_eligible and not now_eligible),
        ))
    return out


def _eligible_after_including(user: User, end_month: Month, this_status: str) -> bool:
    """Eligibility if we include this month's prospective status."""
    window = (Month.objects
              .filter(start_date__lte=end_month.start_date)
              .order_by("-start_date")
              [:6])
    if len(window) < 6:
        return False
    ids = [m.id for m in window]
    got = dict(ComplianceMonthly.objects
               .filter(user=user, month_id__in=ids)
               .values_list("month_id", "status"))
    # inject the prospective status for end_month
    got[end_month.id] = this_status
    return all(got.get(mid) == ComplianceMonthly.ComplianceStatus.COMPLIANT for mid in ids)

# --- B) PERSIST (bulk upsert) ---

@transaction.atomic
def commit_month(month: Month, evals: List[ComplianceEval]) -> int:
    """
    Idempotent write: upsert one row per (user, month).
    Returns number of rows written.
    """
    rows = [
        ComplianceMonthly(
            user_id=e.user_id,
            month_id=e.month_id,
            status=e.status,
            rule_version="v1",          # bump when rules change
            reason=e.reason,
            source="auto",
        ) for e in evals
    ]

    # Django 4.1+: bulk_create with conflict handling
    # If your DB is Postgres, this is efficient.
    created = ComplianceMonthly.objects.bulk_create(
        rows,
        update_conflicts=True,
        update_fields=["status", "reason", "rule_version", "source", "checked_at"],
        unique_fields=["user", "month"],
    )
    return len(created)
