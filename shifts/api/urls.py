from django.urls import path
from .views import MonthImpactView


urlpatterns = [
    path('months/impact/', MonthImpactView.as_view(), name='month-impact'),
]
