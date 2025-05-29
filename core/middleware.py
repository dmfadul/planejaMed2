from django.shortcuts import redirect
from django.urls import reverse
from .models import MaintenanceMode


class MaintenanceMiddleware:
    """
    Middleware to handle maintenance mode.
    If maintenance mode is enabled, it redirects non-staff users to a maintenance notice page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if MaintenanceMode.is_enabled():
            if not request.user.is_authenticated or not request.user.is_staff:
                # Redirect to a maintenance page or a specific URL
                return redirect('maintenance_notice')
        return self.get_response(request)