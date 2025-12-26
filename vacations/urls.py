from django.urls import path
from .views import rights_report, grant_manumission

app_name = "vacations"

urlpatterns = [
    path("report/", rights_report, name="rights_report"),
    path("grant-manumission/", grant_manumission, name="grant_manumission"),
]