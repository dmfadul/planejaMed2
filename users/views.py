from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True  # Redirects already logged-in users
    success_url = reverse_lazy("shifts:dashboard")  # Change this to the actual landing page


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")
    