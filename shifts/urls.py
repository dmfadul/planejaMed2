from django.urls import path
from .views import dashboard

app_name = "shifts"

urlpatterns = [
    path("dashboard", dashboard, name="dashboard"),
]