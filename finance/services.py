from decimal import Decimal
from django.db.models import Sum
from .models import FinanceEntry
from core.models import User
from django.db.models.functions import Lower


SHEET_COLUMNS = [
    ("creditos_individuais", "Cred ind"),
    ("debitos_individuais", "Deb ind"),
    ("aih", "AIH"),
    ("copan", "Copan"),
    ("unimed", "Unimed"),
    ("producao_dividida", "Prod div"),
    ("hospital_ccg", "CCG"),
    ("hospital_cco", "CCO"),
    ("hospital_ccq", "CCQ"),
    ("hospital_sadt", "SADT"),
    ("hospital_eco", "ECO"),
    ("cooperhec", "Cooperhec"),
]


def build_finance_grid(month):
    users = User.objects.filter(is_active=True, is_invisible=False).order_by(Lower("name"))
    print(users)

def sum_entries(entries, *, entry_type=None, category_code=None):
    qs = entries

    if entry_type:
        qs = qs.filter(entry_type=entry_type)

    if category_code:
        qs = qs.filter(category__code=category_code)

    return qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")


def get_user_finance_summary(month, user):
    entries = FinanceEntry.objects.filter(month=month, user=user)

    category_totals = {}

    for code, label in SHEET_COLUMNS:
        category_totals[code] = sum_entries(
            entries,
            category_code=code,
        )

    gross = sum_entries(entries, entry_type=FinanceEntry.EntryType.CREDIT)

    direct_received = sum_entries(
        entries,
        entry_type=FinanceEntry.EntryType.DIRECT_RECEIPT,
    )

    deductions = sum_entries(
        entries,
        entry_type=FinanceEntry.EntryType.DEDUCTION,
    )

    adjustments = sum_entries(
        entries,
        entry_type=FinanceEntry.EntryType.ADJUSTMENT,
    )

    final_due = gross - direct_received - deductions + adjustments

    return {
        "category_totals": category_totals,
        "gross": gross,
        "direct_received": direct_received,
        "deductions": deductions,
        "adjustments": adjustments,
        "final_due": final_due,
    }