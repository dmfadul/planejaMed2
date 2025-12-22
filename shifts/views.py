import json
import logging
from core.models import User
from django.db import transaction
import core.constants as constants
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from shifts.services.table_services import process_table_payload, build_table_data
from shifts.models import ShiftType, ShiftSnapshot, TemplateShift, Shift, Center, Month

logger = logging.getLogger(__name__) 


@login_required
def month_table(request, center_abbr, month_num, year):
    print("Rendering month_table view")
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_num, year=year)

    table_data = build_table_data(
        center=center,
        table_type="MONTH",
        template="month_table",
        month=month
    )

    table_data["status"] = "ORIGINAL" if month.is_locked else "REALIZADO"
    table_data["holidays"] = [h.day for h in month.holidays.all()]

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
    month = get_object_or_404(Month, number=month_num, year=year)

    table_data = build_table_data(
        table_type=f"HORAS-MÉDICO ({month.name.upper()}-{month.year})",
        template="sum_doctors_month",
        month=month
    )

    context = {"table_data": table_data}

    return render(request, "shifts/table.html", context)


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

    table_data = build_table_data(
        center=center,
        month=month,
        table_type=f"HORAS-DIA ({month.name.upper()})",
        template="sum_days_month"
    )
    
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
def update_holiday(request):
    try:
        data = json.loads(request.body)
        month_number = data.get("monthNumber")
        year = data.get("year")
        holiday = data.get("day")

        if not holiday or not month_number or not year:
            return JsonResponse({"error": "Dados insuficientes."}, status=400)

        month = get_object_or_404(Month, number=month_number, year=year)
        month.toggle_holiday(int(holiday))

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@user_passes_test(lambda u: u.is_superuser)
@require_POST
def unlock_month(request):
    from vacations.models import ComplianceHistory

    keepers_id = request.POST.getlist("keep_entitlements[]", [])
    print("keepers_id:", keepers_id)
    
    next_month = Month.objects.next()
    if not next_month:
        raise ValueError("Nenhum mês bloqueado encontrado.")
    
    with transaction.atomic():
        next_month.unlock()

        ComplianceHistory.populate_compliance_history(
            check_type="MONTH",
            keeper_ids=keepers_id
        )

        logger.info(f'{request.user.crm} unlocked month {next_month}')

        messages.success(request, "Mês desbloqueado com sucesso.")
        
    kwargs = {"center_abbr": "CCG",
              "month_num": next_month.number,
              "year": next_month.year}
    
    return redirect("shifts:month_table", **kwargs)
