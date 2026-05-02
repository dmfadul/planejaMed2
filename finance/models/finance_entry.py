from django.db import models


class FinanceSource(models.Model):
    name = models.CharField(max_length=100)
    pays_directly_to_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FinanceCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    

class FinanceEntry(models.Model):
    class EntryType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DIRECT_RECEIPT = "direct_receipt", "Direct receipt"
        DEDUCTION = "deduction", "Deduction"
        ADJUSTMENT = "adjustment", "Adjustment"

    month = models.ForeignKey(
        "shifts.Month",
        on_delete=models.CASCADE,
        related_name="finance_entries"
    )
    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="finance_entries"
    )
    source = models.ForeignKey(
        "FinanceSource",
        on_delete=models.PROTECT,
        related_name="entries"
    )

    category = models.ForeignKey(
        "FinanceCategory",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

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

    class Meta:
        indexes = [
            models.Index(fields=["month", "user"]),
        ]

    def __str__(self):
        return f"{self.user_id} | {self.month_id} | {self.entry_type} | {self.amount}"