from django.urls import path, reverse_lazy
from django.shortcuts import redirect
from .forms import CustomAuthenticationForm as CustomAForm
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView,
    CustomLogoutView,
    UserCreateView,
    ProfileUpdateView,
    maintenance_notice,
    maintenance_status
)

app_name = "core"

urlpatterns = [
    path('', lambda request: redirect('/CCG/', permanent=False)),
    path("login/", CustomLoginView.as_view(authentication_form=CustomAForm), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("user/create/", UserCreateView.as_view(), name="user_create"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("maintenance/", maintenance_notice, name="maintenance_notice"),
    path("maintenance/status/", maintenance_status, name="maintenance_status"),
]

urlpatterns += [
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="core/password_change.html",
            success_url=reverse_lazy("core:password_change_done"),
        ),
        name="password_change"
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="core/password_change_done.html"),
        name="password_change_done"
    ),

]
