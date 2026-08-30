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
                column=column,
                hospital_map=huem_financial_map,
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


def get_cell_value(user, column, hospital_map):
    key = column["key"]
    subcategory = column.get("subcategory", "")

    if key == "user_name":
        return user.name
    
    if key == "crm":
        return getattr(user, "crm", "")
    
    if key.startswith("rp_huem_"):
        return hospital_map.get(
            (user.id, subcategory.casefold()),
            Decimal("0.00"),
        )
 
    return Decimal("0.07")
