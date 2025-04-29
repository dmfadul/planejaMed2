from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render
from core.models import User
import math
import json


@login_required
def basetable(request, center):    
    weekdays = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
    indexes = [math.ceil(int(x)/7) for x in range(1, 36)]
    context = {
        "center": "CCG",
        "table_type": "BASE",
        "template": "basetable",
        "header1": [""] + weekdays * 5,
        "header2": [""] + indexes,
        "doctors": [],
    }

    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        context["doctors"].append({"name": user.name,
                                   "abbr_name": user.abbr_name,
                                   "crm": user.crm,
                                   "shifts": [""] * 35,})

    return render(request, "shifts/table.html", context)


@login_required
def doctor_basetable(request, center, crm):
    weekdays = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]

    user = User.objects.get(crm=crm)
    shifts = {
        weekdays[0]: [""] * 5,
        weekdays[1]: [""] * 5,
        weekdays[2]: [""] * 5,
        weekdays[3]: [""] * 5,
        weekdays[4]: [""] * 5,
        weekdays[5]: [""] * 5,
        weekdays[6]: [""] * 5,
    }

    context = {
    "center": center,
    "table_type": "BASE",
    "template": "doctor_basetable",
    "header1": [""] + [i for i in range(1, 6)],
    "weekdays": weekdays,
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

        print(state)
        # for cell in state.get("selectedCells"):
        #     updates.append({"cellID": cell.get("cellID"), "newValue": 'd'})

        # process info and update database
        # create updates to be send to the frontend

        return JsonResponse({"updates": updates})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
