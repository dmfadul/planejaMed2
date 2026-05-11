from decimal import Decimal
from django.db.models import Sum
from .models import FinanceEntry


def get_user_finance_summary(month, user):
    entries = FinanceEntry.objects.filter(month=month, user=user)

    gross = entries.filter(entry_type=FinanceEntry.EntryType.CREDIT).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    direct_received = entries.filter(entry_type=FinanceEntry.EntryType.DIRECT_RECEIPT).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    deductions = entries.filter(entry_type=FinanceEntry.EntryType.DEDUCTION).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    adjustments = entries.filter(entry_type=FinanceEntry.EntryType.ADJUSTMENT).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    final_due = gross - direct_received - deductions + adjustments

    return {
        "gross": gross,
        "direct_received": direct_received,
        "deductions": deductions,
        "adjustments": adjustments,
        "final_due": final_due,
    }