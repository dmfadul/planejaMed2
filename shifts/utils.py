from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from django.shortcuts import render, get_object_or_404
from .models import TemplateShift as TS
from collections import defaultdict
from core.models import User
from .models import Center, Month
import json


def build_table_data(center, table_type, template, doctor=None):
    table_data = {
        "center": center.abbreviation,
        "month": 0,
        "year": 0,
        "table_type": table_type,
        "template": template,
        "shift_codes": ["-"] + SHIFT_CODES,
        "hour_range": [f"{x:02d}:00" for x in HOUR_RANGE],
    }
    
    if template == "doctor_basetable":
        shifts = TS.objects.filter(user=doctor, center=center).all()
        shifts = translate_to_table(shifts)
        
        table_data["header1"] = []
        for i in range(6):
            if i == 0:
                table_data["header1"].append({"cellID": 'corner1', "label": ""})
                continue
            table_data["header1"].append({"cellID": i, "label": i})

        table_data["weekdays"] = []
        for i, day in enumerate([d[:3] for d in DIAS_SEMANA]):
            table_data["weekdays"].append({"dayID": i, "label": day})

        table_data["doctor"] = {
            "name": doctor.name,
            "abbr_name": doctor.abbr_name,
            "crm":doctor.crm,
            "shifts": shifts,
        }
    elif template == "basetable":
        header1, header2 = Month.gen_headers()
        table_data["header1"] = header1
        table_data["header2"] = header2
        table_data["doctors"] = []

        doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
        for doctor in doctors:
            shifts = TS.objects.filter(user=doctor, center=center).all()
            shifts = translate_to_table(shifts)

            table_data["doctors"].append({"name": doctor.name,
                                          "abbr_name": doctor.abbr_name,
                                          "crm": doctor.crm,
                                          "shifts": shifts,})
    
    return table_data 
    

def translate_to_table(shifts:list) -> dict:
    """Translate shifts to table formatting."""
    if not shifts:
        return {}
    
    crm = shifts[0].user.crm
    shifts_per_day = defaultdict(list)
    for shift in shifts:
        shifts_per_day[(shift.weekday, shift.index)].append((shift.start_time, shift.end_time))

    output = {}
    for (weekday, week_index), hours in shifts_per_day.items():
        code = ""
        for hour in hours:
            code += TS.convert_to_code(*hour)
        
        output[f"cell-{crm}-{weekday}-{week_index}"] = code
    
    return output   