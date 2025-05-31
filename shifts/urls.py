from django.urls import path
from .views import month_table, basetable, doctor_basetable
from .views import sum_days_base, sum_days_month
from .views import update, create_month

app_name = "shifts"

urlpatterns = [
    path("monthtable/<str:center_abbr>/<int:month_num>/<int:year>/", month_table, name="month_table"),
    path("basetable/<str:center_abbr>/", basetable, name="basetable"),
    path("basetable/<str:center_abbr>/<str:crm>/", doctor_basetable, name="doctor_basetable"),
    path("sum-days/<str:center_abbr>/", sum_days_base, name="sum_days_base"),
    path("sum-days/<str:center_abbr>/<int:month_num>/<int:year>/", sum_days_month, name="sum_days_month"),
    path("update", update, name="update"), 
    path("create_month", create_month, name="create_month"),
    ]