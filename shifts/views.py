import logging
from core.models import User
import core.constants as constants
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from shifts.services.table_services import process_table_payload, build_table_data
from shifts.models import ShiftType, ShiftSnapshot, TemplateShift, Shift, Center, Month



logger = logging.getLogger(__name__) 


@login_required
def month_table(request, center_abbr, month_num, year):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_num, year=year)

    status = "ORIGIANAL" if month.is_locked else "REALIZADO"

    table_data = build_table_data(
        center=center,
        table_type="MONTH",
        template="month_table",
        month=month
    )

    table_data["status"] = status
    context = {"table_data": table_data}
    print(table_data.keys())

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
def create_month(request):
    print("Creating new month...")
    next_month = Month.objects.next()
    if next_month:
        raise ValueError(f"Já existe um mês {next_month} criado.")
    
    curr_month = Month.objects.current()
    if not curr_month:
        raise ValueError("Nenhum mês atual encontrado.")
    
    ShiftSnapshot.take_snapshot(curr_month, ShiftType.BASE)
    ShiftSnapshot.take_snapshot(curr_month, ShiftType.ORIGINAL)
       
    next_number, next_year = curr_month.next_number_year()

    new_month = Month.new_month(next_number, next_year)
    new_month.populate_month()
    new_month.fix_users()

    logger.info(f'{request.user.crm} created a new month')
    messages.success(request, "Mês criado com sucesso.")

    kwargs = {"center_abbr": "CCG",
              "month_num": new_month.number,
              "year": new_month.year}

    return redirect("shifts:month_table", **kwargs)


@user_passes_test(lambda u: u.is_superuser)
@require_POST
def unlock_month(request):
    print("Unlocking month...")
    next_month = Month.objects.next()
    if not next_month:
        raise ValueError("Nenhum mês bloqueado encontrado.")
    
    curr_month = Month.objects.current()
    curr_month.is_current = False
    curr_month.save()

    next_month.is_locked = False
    next_month.is_current = True
    
    next_month.save()

    ShiftSnapshot.take_snapshot(next_month, ShiftType.REALIZED)

    messages.success(request, "Mês desbloqueado com sucesso.")
    logger.info(f'{request.user.crm} unlocked month {next_month}')

    kwargs = {"center_abbr": "CCG",
              "month_num": next_month.number,
              "year": next_month.year}
    
    return redirect("shifts:month_table", **kwargs)
