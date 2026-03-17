from django.urls import path
from .views import upload_document_view, finance_dashboard_view

app_name = "finance"

urlpatterns = [
    path("upload/", upload_document_view, name="upload"),
    path("dashboard/", finance_dashboard_view, name="dashboard"),
]