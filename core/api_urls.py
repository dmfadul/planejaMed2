from django.urls import path, include


urlpatterns = [
    path('', include('shifts.api.urls')),
    path('', include('user_requests.api.urls')),
]