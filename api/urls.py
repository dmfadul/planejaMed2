from django.urls import path, include
from . import views

app_name = "api"


urlpatterns = [
    path('', views.apiOverview, name="api-overview"),
    path("submit_user_request/", views.userRequestCreate.as_view(), name="api-submit-user-request"),
    path("hours/", views.get_hours, name="api-hours"),
    path("notifications/", views.notificationsList.as_view(), name="api-notifications"),
    path("users/", views.users_list, name="api-users"),
    path("centers/", views.centers_list, name="api-centers"),
    path("months/", views.month_list, name="api-months"),
    path("years/", views.year_list, name="api-years"),
    path("day_schedule/<str:center_abbr>/<int:year>/<int:month_number>/<int:day>/", views.day_schedule, name="api-day-schedule"),
]
