from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from django.shortcuts import render, get_object_or_404
from .models import TemplateShift as TS
from core.models import User
from .models import Center
import json


def unpack_table_data(request):
    """Update table data based on the request."""

    state = json.loads(request.body)
    table_type = state.get("tableType")
    action = state.get("action")       
    month = state.get("month")
    year = state.get("year")
    center = get_object_or_404(Center, abbreviation=state.get("center"))
    
    updates = []
    new_values = state.get("newValues")
    for cell_id, value in new_values.items():
        _, crm, weekday, idx = cell_id.split("-")
        doctor = User.objects.get(crm=int(crm))
        
        shift_code = value.get("shiftCode")
        start_time = int(value.get("startTime").split(":")[0]) if value.get("startTime") else 0
        end_time = int(value.get("endTime").split(":")[0]) if value.get("endTime") else 0
        
        if shift_code == "-":
            shift_code = TS.convert_to_code(start_time, end_time)
        else:
            start_time, end_time = TS.convert_to_hours(shift_code)
        
        if action == "add" and table_type == "BASE":
            TS.add(doctor=doctor,
                   center=center,
                   week_day=int(weekday),
                   week_index=int(idx),
                   start_time=start_time,
                   end_time=end_time)
        
        updates.append({
            "cellID": cell_id,
            "newValue": shift_code,
        })

    return updates   


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
        shifts = TS.build_doctor_shifts(doctor=doctor, center=center)
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
        header1, header2 = TS.gen_headers()
        table_data["header1"] = header1
        table_data["header2"] = header2
        table_data["doctors"] = []

        doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
        for doctor in doctors:
            shifts = TS.build_doctor_shifts(doctor=doctor, center=center)
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
    for (weekday, week_index), hours in shifts.items():
        code = ""
        for hour in hours:
            code += TS.convert_to_code(*hour)
        
        output[f"cell-{crm}-{weekday}-{week_index}"] = code
    
    return output   