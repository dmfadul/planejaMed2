from django.urls import path, include


urlpatterns = [
    path('', include('shifts.api.urls')),
]