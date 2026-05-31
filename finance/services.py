from decimal import Decimal
from django.db.models import Sum
from .models import FinanceEntry
from core.models import User
from django.db.models.functions import Lower
from finance.grid import FINANCE_GRID_COLUMNS


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
    
    entries = FinanceEntry.objects.filter(month=month).select_related(
        "user",
        "category",
        "source",
    )

    entry_map = {}
    for entry in entries:
        if entry.category:
            entry_map[(entry.user_id, entry.category.code)] = entry.ammount

    rows = []
    for user in users:
        row = {
            "user": user,
            "cells": [],
        }

        for column in FINANCE_GRID_COLUMNS:
            value = get_cell_value(
                user=user,
                month=month,
                column=column,
                entry_map=entry_map,
            )

            row["cells"].append({
                "column": column,
                "value": value,
                "editable": column.get("editable", False),
                "protected": not column.get("editable", False)
            })

        rows.append(row)
    
    return {
        "columns": FINANCE_GRID_COLUMNS,
        "rows": rows,
    }
        

def get_cell_value(user, month, column, entry_map):
    key = column["key"]

    if key == "user_name":
        return user.name
    
    if key == "crm":
        return getattr(user, "crm", "")
    
    # Protected/calculated HUEM cells
    if key.startswith("huem_"):
        return calculate_huem_hours(user, month, key)

    # Editable financial cells
    category_code = column.get("category_code")
    if category_code:
        return entry_map.get((user.id, category_code), Decimal("0.00"))

    return ""


def calculate_huem_hours(user, month, key):
    """
    Later this should read from shifts/appointments.
    For now, return 0 or imported value.
    """
    return Decimal("0.00")



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