from decimal import Decimal
from django.db.models import Sum
from .models import FinanceConstant, FinanceEntry
from core.models import User
from django.db.models.functions import Collate
from core.db.sqlite_collations import COLLATION_NAME
from core.constants import STR_DAY, END_DAY


def build_user_monthly_hours_payload(user, month):
    """
    Returns monthly routine/urgency hours grouped by center
    for the logged-in user only. Used for the "My payment" page.
    """

    data = {
        "doctor": user.name,
        "month": "June/2026",

        "total_payment": 2.23,
        "bonuses": 0,
        "extras": 0,

        "centers": [
            {
                "name": "ECO",
                "routine_hours": 3,
                "urgency_hours": 0,
            },
            {
                "name": "CCG",
                "routine_hours": 0,
                "urgency_hours": 0,
            },
            {
                "name": "CCQ",
                "routine_hours": 0,
                "urgency_hours": 0,
            },
        ],
    }

    return data

def build_constant_grid(rows, month):
    out_rows = []

    for row in rows:
        r = {"cells": []}

        value = get_constant_value(row, month)

        # Column 1: label (not editable)
        r["cells"].append({
            "key": row.get("key"),
            "label": row.get("label", ""),
            "value": row.get("label", ""),
            "editable": False,
            "protected": True,
        })

        # Column 2: value (editable or not)
        r["cells"].append({
            "key": row.get("key"),
            "value": value,
            "editable": row.get("editable", False),
            "protected": not row.get("editable", False),
        })

        out_rows.append(r)

    return {"rows": out_rows}


def build_finance_grid(month, columns):
    users = User.objects.filter(is_active=True, is_invisible=False).order_by(Collate("name", COLLATION_NAME), "id")
    
    entries = FinanceEntry.objects.filter(month=month).select_related(
        "user",
        "category",
        "source",
    )

    entry_map = {}
    for entry in entries:
        if entry.category:
            # the combination of user, category, and description should uniquely identify an entry for the grid
            # which means that the category code + description should uniquely identify a column in the grid
            entry_map[(entry.user_id, entry.category.code, entry.description)] = entry.amount

    rows = []
    for user in users:
        row = {
            "user": user,
            "cells": [],
        }

        for column in columns:
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
        "columns": columns,
        "rows": rows,
    }


def get_constant_value(row, month):    
    code = row["code"]

    if row.get("editable", False):
        # Editable constants should read from FinanceConstant entries
        constant = FinanceConstant.objects.filter(month=month, code=code).first()
        return f"{constant.value:<,.2f}" if constant else Decimal("0.00")

    if code == "period":
        previous_month = month.get_previous()
        return f"{STR_DAY} de {previous_month.name.upper()} a {END_DAY} de {month.name.upper()}"
    if code == "competence":
        return month.name.upper()
    if code == "aih":
        # soma rp_huem_aih_proc do mês
        return 0
    if code == "total_production":
        # + aih
        # + eco_particular_direct
        # + huem_particular_direct
        # + rp_huem_convenios_proc
        # + rp_huem_Ambulatory_proc
        # +(huem_coopan_coops+eco_copan_coops)*redutor
        # +(huem_unimed_coops+eco_unimed_coops)*redutor

        # -adjustments_cash_production
        # -(vacation_hours_rotine+vacation_hours_urgent)*horaHuem
        # -(adm_hours_additional*horaHuem)
        return 0
    if code == "routine_production":
        # =$C$4*$CÁLCULOS.$L$3
        # /($CÁLCULOS.$L$3+$CÁLCULOS.$M$3)
        # PROD_TOTAL * (Nº DE HORAS ROTINA / Nº DE HORAS ROTINA + Nº DE HORAS URGÊNCIA)
        return 0
    if code == "urgency_production":
        # PROD_TOTAL * (Nº DE HORAS URGÊNCIA / Nº DE HORAS ROTINA + Nº DE HORAS URGÊNCIA)
        # NEXT STEP: ADD A TOTAL_HOURS CALCULATION TO THE FINANCE_ENTRY MODEL AND USE IT HERE
        return 0
    if code == "hour_value":
        return 0
    if code == "twelve_hours":
        return 0
    if code == "routine_production_percentage":
        return 0
    if code == "urgency_production_percentage":
        return 0
    if code == "routine_hour_value":
        return 0
    if code == "urgency_hour_value":
        return 0
    if code == "twelve_hours_routine":
        return 0
    if code == "twelve_hours_urgency":
        return 0
    if code == "billing":
        return 0
    
    raise ValueError(f"Unknown constant code: {code}")

def get_cell_value(user, month, column, entry_map):
    key = column["key"]

    if key == "user_name":
        return user.name
    
    if key == "crm":
        return getattr(user, "crm", "")
    
    # Protected/calculated HUEM cells
    # if key.startswith("huem_"):
    if not column.get("editable", False):
        return calculate_hours_from_db(user, month, key)

    # Editable financial cells
    category_code = column.get("category_code")
    description = f"{column.get('subcategory', '')}_{column['label']}"
    if category_code:
        return entry_map.get((user.id, category_code, description), Decimal("0.00"))

    return ""


def calculate_hours_from_db(user, month, key):
    """
    Later this should read from shifts/appointments.
    For now, return 0 or imported value.
    """
    return Decimal("0.00")
