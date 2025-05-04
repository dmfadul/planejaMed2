from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from core.constants import DIAS_SEMANA
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from core.models import User
from .utils import build_table_data
from shifts.models import TemplateShift, Shift, Center
import json


@login_required
def basetable(request, center_abbr):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    table_data = build_table_data(center, "BASE", "basetable")
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def doctor_basetable(request, center_abbr, crm):    
    doctor = get_object_or_404(User, crm=crm)
    center = get_object_or_404(Center, abbreviation=center_abbr)
    table_data = build_table_data(center, "BASE", "doctor_basetable", doctor)
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
@require_POST
def update(request):
    try:
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
                shift_code = TemplateShift.convert_to_code(start_time, end_time)
            else:
                start_time, end_time = TemplateShift.convert_to_hours(shift_code)

            if action == "add" and table_type == "BASE":
                TemplateShift.add(doctor=doctor,
                                  center=center,
                                  week_day=int(weekday),
                                  week_index=int(idx),
                                  start_time=start_time,
                                  end_time=end_time)


            updates.append({
                "cellID": cell_id,
                "newValue": shift_code,
            })   

        return JsonResponse({"updates": updates})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
