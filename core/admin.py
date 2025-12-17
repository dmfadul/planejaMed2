from .models import User, MaintenanceMode
from .admin_forms import UserCreationForm, UserChangeForm

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    ordering = ("crm",)
    list_display = ("crm", "name", "email", "is_active", "is_staff", "is_superuser")
    search_fields = ("crm", "name", "email")
    list_filter = ("is_active", "is_staff", "is_superuser", "is_manager")

    fieldsets = (
        (None, {"fields": ("crm", "password")}),
        (_("Personal info"), {"fields": ("name", "alias", "email", "phone", "rqe")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "is_manager", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("crm", "name", "email", "alias", "phone", "rqe", "password1", "password2", "is_active", "is_staff", "is_superuser", "is_manager"),
        }),
    )

    readonly_fields = ("last_login", "date_joined")


@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ['enabled']