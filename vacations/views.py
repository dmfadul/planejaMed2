from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def report(request):
    return render(request, "vacations/rights_report.html")