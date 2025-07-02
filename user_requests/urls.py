from django.urls import path
from .views import calendar

app_name = "requests"

urlpatterns = [
    path("calendar/<str:center_abbr>/", calendar, name="calendar"),
]