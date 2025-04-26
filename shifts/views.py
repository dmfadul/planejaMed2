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
        "header1": [""] + weekdays * 5,
        "header2": [""] + indexes,
        "doctors": []
    }

    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        context["doctors"].append({"name": user.name,
                                   "crm": user.crm,
                                   "shifts": [""] * 35,})

    return render(request, "shifts/table.html", context)

def doctor_basetable(request, center, crm):
    return HttpResponse("Hello, world. You're at the doctor basetable page.")

@login_required
def dashboard(request):
    return render(request, "shifts/dashboard.html")
