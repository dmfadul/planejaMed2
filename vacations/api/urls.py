from django.urls import path
from vacations.api.views import VacationPay

app_name = "vacations_api"

urlpatterns = [
    path("vacations/pay/", VacationPay.as_view(), name="vacation_pay"),
]
