from django.urls import path
from .views import (
    upload_document_view,
    finance_dashboard,
    finance_spreadsheet,
    edit_cell,
    update_cell,
)

app_name = "finance"

urlpatterns = [
    path("upload/", upload_document_view, name="upload"),
    path("dashboard/", finance_dashboard, name="dashboard"),
    path("spreadsheet/", finance_spreadsheet, name="spreadsheet"),
        path(
        "spreadsheet/<int:month_id>/<int:user_id>/<str:column_key>/edit/",
        edit_cell,
        name="edit_cell",
    ),
    path(
        "spreadsheet/<int:month_id>/<int:user_id>/<str:column_key>/update/",
        update_cell,
        name="update_cell",
    ),
]