from django.urls import path
from .views import report, grant_manumission

app_name = "vacations"

urlpatterns = [
    path("report/", report, name="report"),
    path("grant-manumission/", grant_manumission, name="grant_manumission"),
]