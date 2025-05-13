from .models import TemplateShift as TS
from collections import defaultdict

    
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