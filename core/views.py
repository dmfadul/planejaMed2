from .models import MaintenanceMode
from .forms import ProfileForm

from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import UpdateView

User = get_user_model()


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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "core/profile_update.html"
    success_url = reverse_lazy("core:profile_update")

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


def maintenance_notice(request):
    return render(request, "core/maintenance.html")


def maintenance_status(request):
    return JsonResponse({'enabled': MaintenanceMode.is_enabled()})