from django.urls import path
from .views import dashboard, basetable

app_name = "shifts"

urlpatterns = [
    path("dashboard", dashboard, name="dashboard"),
    path("basetable/<str:center>", basetable, name="basetable"),
]