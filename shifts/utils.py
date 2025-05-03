from core.constants import SHIFT_CODES, HOUR_RANGE
from .models import TemplateShift
from core.models import User
import json


def build_table_data(center, table_type, template):
    table_data = {
        "center": center.abbreviation,
        "table_type": table_type,
        "template": template,
        "shift_codes": json.dumps(["-"] + SHIFT_CODES),
        "hour_range": json.dumps([f"{x:02d}:00" for x in HOUR_RANGE]),
    }
    header1, header2 = TemplateShift.gen_headers()
    table_data["header1"] = header1
    table_data["header2"] = header2
    table_data["doctors"] = []


    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        shifts = TemplateShift.build_doctor_shifts(doctor=user, center=center)
        shifts = translate_to_table(user.crm, shifts)

        table_data["doctors"].append({"name": user.name,
                                      "abbr_name": user.abbr_name,
                                      "crm": user.crm,
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