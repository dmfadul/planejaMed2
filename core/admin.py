from .models import User, MaintenanceMode
from .admin_forms import UserCreationForm, UserChangeForm

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html_join

User = get_user_model()

admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    readonly_fields = ("member_list",)

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "permissions",
                "member_list",
            )
        }),
    )

    @admin.display(description="Members")
    def member_list(self, group):
        if not group.pk:
            return "Save the group before adding members."

        users = User.objects.filter(groups=group).order_by("name")

        if not users.exists():
            return "No members in this group."

        return format_html_join(
            "",
            "<div>{}</div>",
            ((user.name,) for user in users),
        )
    

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    ordering = ("name",)
    list_display = ("crm", "name", "email", "is_active", "is_invisible", "is_staff", "is_superuser")
    search_fields = ("crm", "search_name", "email")
    list_filter = ("is_active", "is_invisible", "is_staff", "is_superuser", "is_manager")

    fieldsets = (
        (None, {"fields": ("crm", "password")}),
        (_("Personal info"), {"fields": ("name", "search_name", "alias", "email", "phone", "rqe")}),
        (_("Permissions"), {"fields": ("is_active", "is_invisible", "is_staff", "is_superuser", "is_manager", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("crm", "name", "email", "alias", "phone", "rqe", "password1", "password2", "is_active", "is_staff", "is_superuser", "is_manager"),
        }),
    )

    readonly_fields = ("search_name", "last_login", "date_joined")


@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ['enabled']