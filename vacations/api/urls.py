from rest_framework.routers import DefaultRouter
from vacations.api.views import VacationViewSet

router = DefaultRouter()
router.register(r'vacation', VacationViewSet, basename='vacation')

urlpatterns = router.urls