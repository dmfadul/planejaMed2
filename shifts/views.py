from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def basetable(request):
    return render(request, "shifts/table.html")


@login_required
def dashboard(request):
    return render(request, "shifts/dashboard.html")
