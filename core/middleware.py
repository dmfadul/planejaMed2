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
        path = request.path
        maintenance_url = reverse('core:maintenance_notice')
        
        if MaintenanceMode.is_enabled():
            if not request.user.is_authenticated or not request.user.is_staff:
                if not path == maintenance_url:
                    return redirect('core:maintenance_notice')
        return self.get_response(request)