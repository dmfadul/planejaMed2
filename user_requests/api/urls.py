from django.urls import path, include
from .views import NotificationViewSet
from rest_framework.routers import DefaultRouter


app_name = "user_requests_api"

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
