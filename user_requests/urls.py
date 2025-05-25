from django.urls import path
from .views import calendar

app_name = "requests"

urlpatterns = [
    path("calendar/", calendar, name="calendar"),
]