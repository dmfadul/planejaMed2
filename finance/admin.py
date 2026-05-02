from django.contrib import admin
from .models import FinanceSource, FinanceEntry


@admin.register(FinanceSource)
class FinanceSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "pays_directly_to_user", "is_active")
    list_filter = ("pays_directly_to_user", "is_active")
    search_fields = ("name",)


@admin.register(FinanceEntry)
class FinanceEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "month", "source", "entry_type", "amount", "created_at")
    list_filter = ("month", "source", "entry_type")
    search_fields = ("user__username", "user__first_name", "user__last_name", "description")