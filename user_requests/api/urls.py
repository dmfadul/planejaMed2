from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRequestAPIView,
    NotificationViewSet,
    VacationRequest
)


app_name = ""

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('vacation-requests/', VacationRequest.as_view(), name='vacation-request'),
    path('user-requests/', UserRequestAPIView.as_view(), name='user-request'),
]
