from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View


class CustomLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True  # Redirects already logged-in users
    success_url = reverse_lazy("user_requests:calendar")  # Change this to the actual landing page


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse_lazy("core:login"))
