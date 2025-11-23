from django.urls import path
from .views import (
    MonthImpactView,
    MonthAPIview,
    CenterAPIview,
    day_schedule,
    get_hours,
)

app_name = "shifts_api"

urlpatterns = [
    path('months/impact/',          MonthImpactView.as_view(), name='month-impact'),
    path('months/<str:selector>/',  MonthAPIview.as_view(), name='month-detail'),
    path('months/',                 MonthAPIview.as_view(), name='months'),
    path('centers/',                CenterAPIview.as_view(), name='center-list'),
    path('centers/<int:pk>/',       CenterAPIview.as_view(), name='center-detail'),
    path('hours/',                  get_hours, name='get-hours'),
    path('day_schedule/<str:center_abbr>/<int:year>/<int:month_number>/<int:day>/', day_schedule, name='day-schedule'),
]
