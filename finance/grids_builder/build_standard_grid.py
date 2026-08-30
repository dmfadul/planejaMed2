from decimal import Decimal
from django.db.models.functions import Collate
from core.db.sqlite_collations import COLLATION_NAME

from core.models import User
from finance.services import build_hospital_financial_map
from finance.models import (
    HospitalFinancialBatch,
    HospitalFinancialEntry
)

def build_income_grid(month, columns):    
    huem_financial_map = build_hospital_financial_map(month, HospitalFinancialBatch.BatchType.ORIGINAL)
    users = User.objects.filter(is_active=True, is_invisible=False).order_by(Collate("name", COLLATION_NAME), "id")

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
                # entry_map=entry_map,
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


def calculate_hours_from_db(user, month, key):
    """
    Later this should read from shifts/appointments.
    For now, return 0 or imported value.
    """

    return Decimal("0.05")


def calculate_hours_from_hospital_data(user, month, batch_type, subcategory):
    """
    Gets hours from huem_financial, that originates from detailed hospital reports.
    """
    print("Calculating hours for user:", user.name, "month:", month, "subcategory:", subcategory)
    entries = HospitalFinancialEntry.objects.filter(
        doctor=user,
        batch__month=month,
        subcategory=subcategory,
    )

    return Decimal("0.05")

def get_cell_value(user, month, column, entry_map=None):
    key = column["key"]
    subcategory = column.get("subcategory", "")

    if key == "user_name":
        return user.name
    
    if key == "crm":
        return getattr(user, "crm", "")
    
    if key.startswith("rp_huem_"):
        return calculate_hours_from_hospital_data(user, month, "original", subcategory)

    print("key:", key, "subcategory:", subcategory)
    return Decimal("0.07")

    
    # if not column.get("editable", False):
    #     return calculate_hours_from_db(user, month, key)

    # # Editable financial cells
    # category_code = column.get("category_code")
    # description = f"{column.get('subcategory', '')}_{column['label']}"
    # if category_code:
    #     return entry_map.get((user.id, category_code, description), Decimal("0.00"))

    # return ""