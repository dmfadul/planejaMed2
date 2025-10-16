from django.urls import path
from .views import calendar, schedule, notifications

app_name = "requests"

urlpatterns = [
    path("calendar/<str:center_abbr>/", calendar, name="calendar"),
    path("schedule/", schedule, name="schedule"),
    path("notifications/", notifications, name="notifications"),
]