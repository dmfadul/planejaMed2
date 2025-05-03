from core.constants import SHIFT_CODES, HOUR_RANGE
import json


def build_table_data(center, table_type, template):
    return {
        "center": center,
        "table_type": table_type,
        "template": template,
        "shift_codes": json.dumps(["-"] + SHIFT_CODES),
        "hour_range": json.dumps([f"{x:02d}:00" for x in HOUR_RANGE]),
    }
    