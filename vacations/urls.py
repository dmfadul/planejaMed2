from django.urls import path
from .views import report

app_name = "vacations"

urlpatterns = [
    path("report/", report, name="report"),
]