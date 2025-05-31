from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from core.constants import DIAS_SEMANA
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.models import User
from .table_payload import process_table_payload
from .table_builder import build_table_data
from shifts.models import TemplateShift, Shift, Center, Month
from django.contrib import messages
import json


@login_required
def month_table(request, center_abbr, month_num, year):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_num, year=year)
    table_data = build_table_data(center, "MONTH", "month_table", month=month)
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def basetable(request, center_abbr):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    table_data = build_table_data(center, "BASE", "basetable")
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def doctor_basetable(request, center_abbr, crm):    
    doctor = get_object_or_404(User, crm=crm)
    center = get_object_or_404(Center, abbreviation=center_abbr)
    table_data = build_table_data(center, "BASE", "doctor_basetable", doctor)
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def sum_days_base(request, center_abbr):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    table_data = build_table_data(center, "BASE", "sum_days_base")
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def sum_days_month(request, center_abbr, month_num, year):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_num, year=year)
    table_data = build_table_data()
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@user_passes_test(lambda u: u.is_superuser)
@require_POST
def update(request):
    try:
        updates = process_table_payload(request)
        return JsonResponse({"updates": updates})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@user_passes_test(lambda u: u.is_superuser)
def create_month(request):
    if request.method == "POST":
        print("Creating month...")

        messages.success(request, "Mês criado com sucesso.")

    return redirect(request.META.get("HTTP_REFERER", "/"))