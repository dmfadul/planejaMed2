from django.urls import path
from .views import upload_document_view, finance_dashboard, finance_spreadsheet

app_name = "finance"

urlpatterns = [
    path("upload/", upload_document_view, name="upload"),
    path("dashboard/", finance_dashboard, name="dashboard"),
    path("spreadsheet/", finance_spreadsheet, name="spreadsheet"),
]