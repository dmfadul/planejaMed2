from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import User
import math

from django.http import HttpResponse 


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
def dashboard(request):
    return render(request, "shifts/dashboard.html")
