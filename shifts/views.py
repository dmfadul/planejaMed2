from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from core.constants import DIAS_SEMANA
from django.http import JsonResponse
from django.shortcuts import render
from core.models import User
from .utils import build_table_data
from shifts.models import TemplateShift, Shift, Center
import json


WEEKDAYS = [d[:3] for d in DIAS_SEMANA]


@login_required
def basetable(request, center):
    table_data = build_table_data(center, "BASE", "basetable")
    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        table_data["doctors"].append({"name": user.name,
                                      "abbr_name": user.abbr_name,
                                      "crm": user.crm,
                                      "shifts": [""] * 35,})

    return render(request, "shifts/table.html", table_data)


@login_required
def doctor_basetable(request, center, crm):    
    user = User.objects.get(crm=crm)
    shifts = {
        WEEKDAYS[0]: [""] * 5,
        WEEKDAYS[1]: [""] * 5,
        WEEKDAYS[2]: [""] * 5,
        WEEKDAYS[3]: [""] * 5,
        WEEKDAYS[4]: [""] * 5,
        WEEKDAYS[5]: [""] * 5,
        WEEKDAYS[6]: [""] * 5,
    }

    context = {
        "center": center,
        "table_type": "BASE",
        "template": "doctor_basetable",
        "header1": [""] + [i for i in range(1, 6)],
        "weekdays": WEEKDAYS,
        "doctor": user,
        "shifts": shifts.items(),
    }

    return render(request, "shifts/doctor_basetable.html", context)


@login_required
@require_POST
def update(request):
    try:
        state = json.loads(request.body)

        table_type = state.get("tableType")
        action = state.get("action")
        
        month = state.get("month")
        year = state.get("year")
        center = Center.objects.get(abbreviation="CCG")
        if not center:
            return JsonResponse({"error": "Center not found"}, status=404)


        updates = []
        new_values = state.get("newValues")
        for cell_id, value in new_values.items():
            _, crm, idx = cell_id.split("-")

            doctor = User.objects.get(crm=int(crm))
            shift_code = value.get("shiftCode")
            start_time = value.get("startTime")
            end_time = value.get("endTime")

            if shift_code == "-":
                shift_code = TemplateShift.convert_to_code(start_time, end_time)
            else:
                start_time, end_time = TemplateShift.convert_to_hours(shift_code)

            if action == "add" and table_type == "BASE":
                TemplateShift.add_shift(doctor=doctor,
                                        center=center,
                                        idx=int(idx),
                                        start_time=start_time,
                                        end_time=end_time)


            updates.append({
                "cellID": cell_id,
                "newValue": shift_code,
            })
            

        return JsonResponse({"updates": updates})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
