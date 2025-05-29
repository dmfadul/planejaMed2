from django.urls import path
from .views import CustomLoginView, CustomLogoutView, maintenance_notice, maintenance_status

app_name = "core"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("maintenance/", maintenance_notice, name="maintenance_notice"),
    path("maintenance/status/", maintenance_status, name="maintenance_status"),
]