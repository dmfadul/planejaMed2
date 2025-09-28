from django.contrib import admin
from .models import UserRequest, Notification


admin.site.register(UserRequest)
admin.site.register(Notification)

