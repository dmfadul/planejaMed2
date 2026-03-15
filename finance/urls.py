from django.urls import path
from .views import upload_view

app_name = "finance"

urlpatterns = [
    path("upload/", upload_view, name="upload"),
]