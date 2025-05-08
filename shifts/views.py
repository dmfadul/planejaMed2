from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from core.constants import DIAS_SEMANA
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from core.models import User
from .table_payload import process_table_payload
from .utils import build_table_data
from shifts.models import TemplateShift, Shift, Center
import json


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
@require_POST
def update(request):
    try:
        updates = process_table_payload(request)
        return JsonResponse({"updates": updates})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
