
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.models import User 


@user_passes_test(lambda u: u.is_superuser)
def rights_report(request):
    users = sorted(User.objects.filter(is_active=True, is_invisible=False).all(), key=lambda u: u.name)
    return render(request, "vacations/rights_report.html", {"users": users})


@user_passes_test(lambda u: u.is_superuser)
def vacations_dashboard(request):
    print("Accessing vacations dashboard")

    return render(request, "vacations/vacations_dashboard.html", context={
        "vacations": [],
        "user_is_admin": request.user.is_superuser,
        "user_is_root": request.user.is_root
    })


@require_POST
def grant_manumission(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    crm = payload.get("crm")
    print("CRM received:", crm)
    # TODO: implement the manumission logic here

    return JsonResponse({"message": "CRM received", "crm": crm})
