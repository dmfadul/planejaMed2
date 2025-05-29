from django.contrib import admin
from .models import User, MaintenanceMode


admin.site.register(User)
@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ['enabled']