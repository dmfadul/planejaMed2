from django.urls import path
from .views import (
    finance_constants,
    upload_document_view,
    user_finance_monthly_data,
    finance_spreadsheet,
    edit_cell,
    update_cell,
    edit_constant_cell,
    update_constant_cell,
)

app_name = "finance"

urlpatterns = [
    path("upload/", upload_document_view, name="upload"),
    path("spreadsheet/", finance_spreadsheet, name="spreadsheet"),
    path("monthly/data/", user_finance_monthly_data, name="monthly_finance_data"),
    path("constants/", finance_constants, name="constants"),
    path(
        "spreadsheet/constants/<int:month_id>/<str:row_key>/edit/",
        edit_constant_cell,
        name="edit_constant_cell",
    ),
    path(
        "spreadsheet/constants/<int:month_id>/<str:row_key>/update/",
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