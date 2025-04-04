from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def basetable(request):
    context = {
        "header1": [""] + ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"] * 5,
        "header2": [""] + [str(i) * 7 for i in range(1, 6)],                           
    }

    return render(request, "shifts/table.html", context)


@login_required
def dashboard(request):
    return render(request, "shifts/dashboard.html")
