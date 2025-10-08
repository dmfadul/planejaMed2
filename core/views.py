from shifts.models import Center
from django.views import View
from .models import MaintenanceMode
from django.http import JsonResponse
from django.contrib.auth import logout
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True  # Redirects already logged-in users
    success_url = reverse_lazy("requests:calendar", kwargs={'center_abbr': "CCG"})
    
    def get_success_url(self):
        return reverse("requests:calendar", kwargs={'center_abbr': "CCG"})
    
class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse_lazy("core:login"))


def maintenance_notice(request):
    return render(request, "core/maintenance.html")


def maintenance_status(request):
    return JsonResponse({'enabled': MaintenanceMode.is_enabled()})