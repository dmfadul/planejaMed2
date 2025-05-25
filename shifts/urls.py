from django.urls import path
from .views import month_table, basetable, doctor_basetable, update, create_month

app_name = "shifts"

urlpatterns = [
    path("monthtable/<str:center_abbr>/<int:month_num>/<int:year>/", month_table, name="month_table"),
    path("basetable/<str:center_abbr>/", basetable, name="basetable"),
    path("basetable/<str:center_abbr>/<str:crm>/", doctor_basetable, name="doctor_basetable"),
    path("update", update, name="update"), 
    path("create_month", create_month, name="create_month"),
    ]