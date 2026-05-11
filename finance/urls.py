from django.urls import path
from .views import upload_document_view, finance_dashboard

app_name = "finance"

urlpatterns = [
    path("upload/", upload_document_view, name="upload"),
    path("dashboard/<int:month_id>/", finance_dashboard, name="dashboard"),
]