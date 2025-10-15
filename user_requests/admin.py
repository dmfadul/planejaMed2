from django.contrib import admin
from .models import UserRequest, Notification, IncludeRequestData


admin.site.register(UserRequest)
admin.site.register(Notification)
admin.site.register(IncludeRequestData)

