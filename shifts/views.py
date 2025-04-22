from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import User
import math


def basetable(request, center):    
    context = {
        "header1": [""] + ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"] * 5,
        "header2": [""] + [math.ceil(int(x)/7) for x in range(1, 36)],
        "table": []
    }

    users = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    for user in users:
        line = [user.name] + [""] * (len(context["header1"]) - 1)
        context["table"].append(line)

    for line in context["table"]:
        print(line)

    return render(request, "shifts/table.html", context)


@login_required
def dashboard(request):
    return render(request, "shifts/dashboard.html")
