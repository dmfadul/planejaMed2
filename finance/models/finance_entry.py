from django.db import models


class FinanceEntry(models.Model):
    class EntryType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DIRECT_RECEIPT = "direct_receipt", "Direct receipt"
        DEDUCTION = "deduction", "Deduction"
        ADJUSTMENT = "adjustment", "Adjustment"

    month = models.ForeignKey("shifts.Month", on_delete=models.CASCADE)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    source = models.ForeignKey("FinanceSource", on_delete=models.PROTECT)

    entry_type = models.CharField(max_length=30, choices=EntryType.choices)
    description = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    imported_document = models.ForeignKey(
        "finance.UploadedDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)