from django.contrib import admin
from .models import (
    FinanceConstant,
    FinanceSource,
    FinanceEntry,
    FinanceCategory,
    HospitalFinancialBatch,
    HospitalFinancialEntry
)


@admin.register(FinanceConstant)
class FinanceConstantAdmin(admin.ModelAdmin):
    list_display = ("month", "code", "label", "value", "order")
    list_filter = ("month",)
    search_fields = ("code", "label")


@admin.register(FinanceSource)
class FinanceSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "pays_directly_to_user", "is_active")
    list_filter = ("pays_directly_to_user", "is_active")
    search_fields = ("name",)


@admin.register(FinanceCategory)
class FinanceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(FinanceEntry)
class FinanceEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "month", "source", "entry_type", "amount", "created_at")
    list_filter = ("month", "source", "entry_type")
    search_fields = ("user__username", "user__first_name", "user__last_name", "description")


class HospitalFinancialEntryInline(admin.TabularInline):
    model = HospitalFinancialEntry
    extra = 0
    show_change_link = True

    fields = (
        "row_number",
        "provider_name",
        "health_plan_name",
        "procedure_description",
        "transfer_description",
        "amount",
    )

    readonly_fields = (
        "row_number",
        "provider_name",
        "health_plan_name",
        "procedure_description",
        "transfer_description",
    )

@admin.register(HospitalFinancialBatch)
class HospitalFinancialBatchAdmin(admin.ModelAdmin):
    list_display = (
        "month",
        "batch_type",
        "version",
        "source_batch",
        "is_final",
        "created_at",
        "created_by",
    )

    list_filter = (
        "batch_type",
        "is_final",
        "month__year",
        "month__number",
    )

    search_fields = (
        "uploaded_document__file",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "source_batch",
        "created_by",
    )

    inlines = [
        HospitalFinancialEntryInline,
    ]

@admin.register(HospitalFinancialEntry)
class HospitalFinancialEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "batch",
        "row_number",
        "provider_name",
        "health_plan_name",
        "amount",
    )

    list_filter = (
        "batch__batch_type",
        "batch__month__year",
        "batch__month__number",
        "health_plan_name",
    )

    search_fields = (
        "provider_name",
        "health_plan_name",
        "procedure_description",
        "transfer_description",
    )

    autocomplete_fields = (
        "batch",
        "source_entry",
    )

    list_select_related = (
        "batch",
        "batch__month",
    )