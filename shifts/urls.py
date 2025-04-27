from django.urls import path
from .views import basetable, doctor_basetable

app_name = "shifts"

urlpatterns = [
    path("basetable/<str:center>", basetable, name="basetable"),
    path("basetable/<str:center>/<str:crm>", doctor_basetable, name="doctor_basetable"),
]