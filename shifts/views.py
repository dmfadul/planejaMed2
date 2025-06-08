import logging
import core.constants as constants
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.models import User
from .table_payload import process_table_payload
from .table_builder import build_table_data
from shifts.models import ShiftType, ShiftSnapshot, TemplateShift, Shift, Center, Month
from django.contrib import messages

logger = logging.getLogger(__name__) 


@login_required
def month_table(request, center_abbr, month_num, year):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_num, year=year)

    table_data = build_table_data(
        center=center,
        table_type="MONTH",
        template="month_table",
        month=month
    )

    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def basetable(request, center_abbr):
    center = get_object_or_404(Center, abbreviation=center_abbr)

    table_data = build_table_data(
        center=center,
        table_type="BASE",
        template="basetable"
    )
    
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def doctor_basetable(request, center_abbr, crm):    
    doctor = get_object_or_404(User, crm=crm)
    center = get_object_or_404(Center, abbreviation=center_abbr)
    
    table_data = build_table_data(
        center=center,
        table_type="BASE",
        template="doctor_basetable",
        doctor=doctor
    )
    
    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def sum_doctors_base(request):
    table_data = build_table_data(
        table_type="HORAS-MÉDICO (BASE)",
        template="sum_doctors_base"
    )

    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


@login_required
def sum_doctors_month(request, month_num, year):
    pass


@login_required
def sum_days_base(request, center_abbr):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    
    table_data = build_table_data(
        center=center,
        table_type="HORAS-DIA (BASE)",
        template="sum_days_base"
    )
    
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
@require_POST
def create_month(request):
    temp_month = Month.new_month(number=constants.FIRST_MONTH, year=constants.FIRST_YEAR)

    ShiftSnapshot.take_snapshot(temp_month, ShiftType.BASE)

    # current_month = Month.get_current()

    
    logger.info(f'{request.user.crm} created a new month')

    messages.success(request, "Mês criado com sucesso.")

    return redirect(request.META.get("HTTP_REFERER", "/"))