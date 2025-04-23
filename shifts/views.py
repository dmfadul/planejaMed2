from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import User
import math


def basetable(request, center):    
    weekdays = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
    indexes = [math.ceil(int(x)/7) for x in range(1, 36)]
    context = {
        
        "header1": [""] + weekdays * 5,
        "header2": [""] + indexes,
        "doctors": []
    }

    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        context["doctors"].append({"name": user.first_name,
                                   "shifts": [""] * 35,})

    return render(request, "shifts/table.html", context)


@login_required
def dashboard(request):
    return render(request, "shifts/dashboard.html")
