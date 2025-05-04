from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from .models import TemplateShift
from core.models import User
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
        shifts = TemplateShift.build_doctor_shifts(doctor=doctor, center=center)
        shifts = translate_to_table(doctor.crm, shifts)
        
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
        header1, header2 = TemplateShift.gen_headers()
        table_data["header1"] = header1
        table_data["header2"] = header2
        table_data["doctors"] = []

        doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
        for doctor in doctors:
            shifts = TemplateShift.build_doctor_shifts(doctor=doctor, center=center)
            shifts = translate_to_table(doctor.crm, shifts)

            table_data["doctors"].append({"name": doctor.name,
                                          "abbr_name": doctor.abbr_name,
                                          "crm": doctor.crm,
                                          "shifts": shifts,})
    
    return table_data 
    

def translate_to_table(crm, shifts):
    """Translate shifts to table formatting."""
    if not shifts:
        return {}

    output = {}
    for day, hours in shifts.items():
        weekday, week_index = day
        start_time, end_time = hours
        output[f"cell-{crm}-{weekday}-{week_index}"] = TemplateShift.convert_to_code(start_time, end_time)
    
    return output   