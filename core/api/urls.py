from django.urls import path, include
from .views import users_list

urlpatterns = [
    path('users/', users_list, name='users_list'),
    path('', include('vacations.api.urls')),
]
