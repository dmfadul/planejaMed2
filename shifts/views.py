from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import math


def basetable(request):
    header = [""] + [str(i) * 7 for i in range(1, 6)],
    print(header)
    context = {
        "header1": [""] + ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"] * 5,
        "header2": [""] + [math.ceil(int(x)/7) for x in range(1, 36)],
    }

    return render(request, "shifts/table.html", context)


@login_required
def dashboard(request):
    return render(request, "shifts/dashboard.html")
