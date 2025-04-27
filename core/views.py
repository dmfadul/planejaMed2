from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render


class CustomLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True  # Redirects already logged-in users
    success_url = reverse_lazy("shifts:dashboard")  # Change this to the actual landing page


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("core:login")


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")