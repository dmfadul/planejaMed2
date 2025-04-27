from django.urls import path
from .views import CustomLoginView, CustomLogoutView, dashboard

app_name = "core"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("dashboard", dashboard, name="dashboard"),
]