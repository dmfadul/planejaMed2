from decimal import Decimal
from core.models import User
from finance.models import FinanceEntry
from django.db.models.functions import Collate
from core.db.sqlite_collations import COLLATION_NAME


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

def calculate_hours_from_db(user, month, key):
    """
    Later this should read from shifts/appointments.
    For now, return 0 or imported value.
    """
    return Decimal("0.01")

def get_cell_value(user, month, column, entry_map):
    key = column["key"]
    print("======================(())")
    print("column", column)
    print("entry_map", entry_map)
    print("======================**")


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
    print("category_code", category_code)
    description = f"{column.get('subcategory', '')}_{column['label']}"
    if category_code:
        return entry_map.get((user.id, category_code, description), Decimal("0.00"))

    return ""