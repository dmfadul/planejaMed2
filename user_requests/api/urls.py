from django.urls import path, include
from .views import NotificationViewSet, VacationRequest
from rest_framework.routers import DefaultRouter


app_name = ""

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('vacation-requests/', VacationRequest.as_view(), name='vacation-request'),
]
