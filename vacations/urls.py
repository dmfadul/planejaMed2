from django.urls import path
from .views import (
    rights_report,
    vacations_dashboard,
    grant_manumission
)

app_name = "vacations"

urlpatterns = [
    path("report/", rights_report, name="rights_report"),
    path("dashboard/", vacations_dashboard, name="vacations_dashboard"),
    path("grant-manumission/", grant_manumission, name="grant_manumission"),
]