from django.urls import path
from .views import MonthImpactView, MonthAPIview, CenterAPIview


urlpatterns = [
    path('months/impact/',          MonthImpactView.as_view(), name='month-impact'),
    path('months/<str:selector>/',  MonthAPIview.as_view(), name='month-detail'),
    path('centers/',                CenterAPIview.as_view(), name='center-list'),
    path('centers/<int:pk>/',       CenterAPIview.as_view(), name='center-detail'),
]
