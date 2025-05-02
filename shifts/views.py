from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from core.constants import DIAS_SEMANA, SHIFT_CODES, HOUR_RANGE
from django.http import JsonResponse
from django.shortcuts import render
from core.models import User
import math
import json


WEEKDAYS = [d[:3] for d in DIAS_SEMANA]


def gen_context(center, table_type, template):
    return {
        "center": center,
        "table_type": table_type,
        "template": template,
        "header1": [""] + WEEKDAYS * 5,
        "shift_codes": json.dumps(["-"] + SHIFT_CODES),
        "hour_range": json.dumps([f"{x:02d}:00" for x in HOUR_RANGE]),
    }


@login_required
def basetable(request, center):
    indexes = [math.ceil(int(x)/7) for x in range(1, 36)]
    context = gen_context(center, "BASE", "basetable")
    context["header2"] = [""] + indexes
    context["doctors"] = []

    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        context["doctors"].append({"name": user.name,
                                   "abbr_name": user.abbr_name,
                                   "crm": user.crm,
                                   "shifts": [""] * 35,})

    return render(request, "shifts/table.html", context)


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
        updates = []

        table_type = state.get("tableType")
        action = state.get("action")
        center = state.get("center")
        month = state.get("month")
        year = state.get("year")

        new_values = state.get("newValues")

        print(table_type)
        print(action)
        print(center)
        print(month)
        print(year)

        for cell_id, value in new_values.items():
            print(cell_id, value)

        # process info and update database
        # create updates to be send to the frontend

        return JsonResponse({"updates": updates})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
