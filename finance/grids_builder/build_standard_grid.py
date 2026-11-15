from decimal import Decimal, InvalidOperation

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from decimal import Decimal
from django.db.models.functions import Collate
from core.db.sqlite_collations import COLLATION_NAME


from core.models import User
from finance.services import build_hospital_financial_map
from finance.models import (
    FinanceEntry,
    FinanceCategory,
    FinanceSource,
    HospitalFinancialBatch,
    HospitalFinancialEntry
)

from shifts.models import Month

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
                month=month,
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


def get_editable_cell_value(user, column, month, raw_value=0):
    category = FinanceCategory.objects.filter(
        name=column["category"],
        code=column["category_code"],
    ).first()

    source = FinanceSource.objects.filter(name=column["source"]).first()   
    if source is None:
        return HttpResponseBadRequest("Invalid source")

    entry = FinanceEntry.objects.filter(
        month=month,
        user=user,
        category=category,
        description=f"{column['subcategory']}_{column['label']}",
        entry_type=column["entry_type"],
        source=source,
    ).first()

    if entry is None:
        return Decimal("0.00")
    
    return entry.amount

def get_cell_value(user, column, month, hospital_map):
    key = column["key"]
    is_editable = column.get("editable", False)

    if is_editable:
        return get_editable_cell_value(user, column, month)

    if key == "user_name":
        return user.name
    
    if key == "crm":
        return getattr(user, "crm", "")
    
    return hospital_map.get(
        (user.id, key.casefold()),
        Decimal("0.00"),
    )