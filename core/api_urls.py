from django.urls import path, include


urlpatterns = [
    path('', include('core.api.urls')),
    path('', include('shifts.api.urls')),
    path('', include('user_requests.api.urls')),
]