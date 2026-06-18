from django.urls import path
from .views import (
    finance_constants,
    upload_document_view,
    finance_spreadsheet,
    edit_cell,
    update_cell,
    update_constant_cell,
)

app_name = "finance"

urlpatterns = [
    path("upload/", upload_document_view, name="upload"),
    path("spreadsheet/", finance_spreadsheet, name="spreadsheet"),
    path("constants/", finance_constants, name="constants"),
    path(
        "spreadsheet/constants/<str:grid_key>/<int:month_id>/<int:user_id>/<str:column_key>/update/",
        update_constant_cell,
        name="update_constant_cell",
    ),
    path(
        "spreadsheet/<str:grid_key>/<int:month_id>/<int:user_id>/<str:column_key>/edit/",
        edit_cell,
        name="edit_cell",
    ),
    path(
        "spreadsheet/<str:grid_key>/<int:month_id>/<int:user_id>/<str:column_key>/update/",
        update_cell,
        name="update_cell",
    ),
]