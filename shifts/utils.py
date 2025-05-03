from core.constants import SHIFT_CODES, HOUR_RANGE
from .models import TemplateShift
import json


def build_table_data(center, table_type, template):
    table_data = {
        "center": center,
        "table_type": table_type,
        "template": template,
        "shift_codes": json.dumps(["-"] + SHIFT_CODES),
        "hour_range": json.dumps([f"{x:02d}:00" for x in HOUR_RANGE]),
    }
    header1, header2 = TemplateShift.gen_headers()
    table_data["header1"] = header1
    table_data["header2"] = header2
    table_data["doctors"] = []
    
    return table_data 
    