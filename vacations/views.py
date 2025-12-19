
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.models import User 


@user_passes_test(lambda u: u.is_superuser)
def report(request):
    users = sorted(User.objects.filter(is_active=True, is_invisible=False).all(), key=lambda u: u.name)
    return render(request, "vacations/rights_report.html", {"users": users})


@require_POST
def grant_manumission(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    crm = payload.get("crm")
    print("CRM received:", crm)

    return JsonResponse({"message": "CRM received", "crm": crm})
