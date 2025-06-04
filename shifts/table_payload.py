import json
from core.models import User
from .utils import translate_to_table
from .models import TemplateShift as TS
from .models import Center, Month, Shift
from django.shortcuts import get_object_or_404


def process_table_payload(request):
    """Update table data based on the request."""

    state = json.loads(request.body)
    action = state.get("action")   
    table_type = state.get("tableType")
    
    if action == "add":
        updates = add_shift(state, table_type)
    elif action == "remove":
        updates = remove_shift(state, table_type)
    else:
        raise ValueError("Improper action or table type.")

    return updates


def remove_shift(state, table_type):
    center = get_object_or_404(Center, abbreviation=state.get("center"))
    
    updates = []
    for cell in state.get("selectedCells"):
        cell_id = cell.get("cellID")
        _, crm, weekday, week_index = cell_id.split("-")
        doctor = User.objects.get(crm=int(crm))

        if table_type == "BASE":
            shifts = TS.objects.filter(
                user=doctor,
                center=center,
                weekday=int(weekday),
                index=int(week_index),
            )

        elif table_type == "MONTH":
            day = int(week_index)
            year = state.get("year")
            number = state.get("month")
            month = get_object_or_404(Month, number=int(number), year=int(year))

            shifts = Shift.objects.filter(
                user=doctor,
                center=center,
                month=month,
                day=day,
            )

        if not shifts:
            return []
        
        for shift in shifts:
            shift.delete()

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
        _, crm, weekday, idx = cell_id.split("-")
        doctor = User.objects.get(crm=int(crm)) 
        
        shift_code = value.get("shiftCode")
        if shift_code == "-":
            start_time = int(value.get("startTime", 0))
            end_time = int(value.get("endTime", 0))
        else:
            start_time, end_time = TS.convert_to_hours(shift_code)

        if table_type == "BASE":
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
            day = int(idx)
            year = state.get("year")
            number = state.get("month")

            month = get_object_or_404(Month, number=int(number), year=int(year))
            Shift.add(doctor=doctor,
                      center=center,
                      month=month,
                      day=day,
                      start_time=start_time,
                      end_time=end_time)
            
            new_shifts = Shift.objects.filter(
                user=doctor,
                center=center,
                month=month,
                day=day,
            ).all()

        new_shifts = translate_to_table(new_shifts)
        
        updates.append({
            "cellID": cell_id,
            "newValue": new_shifts.get(cell_id),
        })

    return updates
