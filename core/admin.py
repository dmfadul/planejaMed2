from django.contrib import admin
from .models import User, MaintenanceMode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


admin.site.register(User)
@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ['enabled']