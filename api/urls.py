from django.urls import path
from . import views

app_name = "api"


urlpatterns = [
    path("centers/", views.centers_list, name="api-centers"),
    path("months/", views.month_list, name="api-months"),
    path("years/", views.year_list, name="api-years"),
    path("day_schedule/<str:center_abbr>/<int:year>/<int:month_number>/<int:day>/", views.day_schedule, name="api-day-schedule"),
]
