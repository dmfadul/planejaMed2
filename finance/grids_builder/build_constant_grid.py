from decimal import Decimal
from finance.models import FinanceConstant
from core.constants import STR_DAY, END_DAY


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
    if code == "overtime_production":
        # PROD_TOTAL * (Nº DE HORAS URGÊNCIA / Nº DE HORAS ROTINA + Nº DE HORAS URGÊNCIA)
        # NEXT STEP: ADD A TOTAL_HOURS CALCULATION TO THE FINANCE_ENTRY MODEL AND USE IT HERE
        return 0
    if code == "hour_value":
        return 0
    if code == "twelve_hours":
        return 0
    if code == "routine_production_percentage":
        return 0
    if code == "overtime_production_percentage":
        return 0
    if code == "routine_hour_value":
        return 0
    if code == "overtime_hour_value":
        return 0
    if code == "twelve_hours_routine":
        return 0
    if code == "twelve_hours_overtime":
        return 0
    if code == "billing":
        return 0
    
    raise ValueError(f"Unknown constant code: {code}")