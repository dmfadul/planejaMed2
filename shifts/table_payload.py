import json
from .models import Center
from core.models import User
from collections import defaultdict
from .models import TemplateShift as TS
from django.shortcuts import get_object_or_404


def process_table_payload(request):
    """Update table data based on the request."""

    state = json.loads(request.body)
    action = state.get("action")   
    table_type = state.get("tableType")
    
    if action == "add" and table_type == "BASE":
        updates = add_shift(state, "BASE")
    elif action == "add" and table_type == "MONTH":
        updates = []
    elif action == "remove" and table_type == "BASE":
        updates = remove_shift(state, "BASE")
    elif action == "remove" and table_type == "MONTH":
        updates = []
    else:
        raise ValueError("Improper action or table type.")

    return updates


def remove_shift(state, table_type):
    print("s", state)
    center = get_object_or_404(Center, abbreviation=state.get("center"))
    
    updates = []
    for cell in state.get("selectedCells"):
        cell_id = cell.get("cellID")
        crm = cell_id.split("-")[1]
        doctor = User.objects.get(crm=int(crm))

        if table_type == "BASE":
            _, _, weekday, week_index = cell_id.split("-")

            shifts = TS.objects.filter(
                user=doctor,
                center=center,
                weekday=int(weekday),
                index=int(week_index),
            )

            for shift in shifts:
                shift.delete()

        elif table_type == "MONTH":
            return []

        updates.append({
            "cellID": cell_id,
            "newValue": "",
        })

    return updates

def add_shift(state, table_type):
    center = get_object_or_404(Center, abbreviation=state.get("center"))
    new_values = state.get("newValues")

    updates = []
    for cell_id, value in new_values.items():       
        shift_code = value.get("shiftCode")
        if not shift_code == "-":
            start_time, end_time = TS.convert_to_hours(shift_code)
        else:
            print(value.get("startTime"), value.get("endTime"))
            start_time = int(value.get("startTime", 0))
            end_time = int(value.get("endTime", 0))

        if table_type == "BASE":
            _, crm, weekday, idx = cell_id.split("-")
            doctor = User.objects.get(crm=int(crm))
            
            TS.add(doctor=doctor,
                   center=center,
                   week_day=int(weekday),
                   week_index=int(idx),
                   start_time=start_time,
                   end_time=end_time)

            new_shifts = TS.objects.filter(
                user=doctor,
                center=center,
                weekday=int(weekday),
                index=int(idx),
            ).all()
        elif table_type == "MONTH":
            return []

        new_shifts = translate_to_table(new_shifts)
        
        updates.append({
            "cellID": cell_id,
            "newValue": new_shifts.get(cell_id),
        })

    return updates


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