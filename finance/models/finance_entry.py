from django.db import models


# Even though this is called "source", it can represent
# both sources of credit and a "source" (destination) of debit,
# For example, "Unimed" can be a source of credit, while "Personnel" is a source of debit.
class FinanceSource(models.Model):
    name = models.CharField(max_length=100)
    pays_directly_to_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# First level of classification for entries
class FinanceCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    

class FinanceEntry(models.Model):
    class EntryType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DIRECT_RECEIPT = "direct_receipt", "Direct receipt"
        DEDUCTION = "deduction", "Deduction"
        ADJUSTMENT = "adjustment", "Adjustment"

    # The fiscal month to which this entry belongs.  
    month = models.ForeignKey(
        "shifts.Month",
        on_delete=models.CASCADE,
        related_name="finance_entries"
    )

    # The user to whom this entry belongs.
    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="finance_entries"
    )

    # The source of this entry. It can be a source of credit or a source of debit, i.e. a payer (like Unimed) or a payee (like Personnel).
    source = models.ForeignKey(
        "FinanceSource",
        on_delete=models.PROTECT,
        related_name="entries"
    )

    # The category of this entry (). This field seems to be the most important.
    category = models.ForeignKey(
        "FinanceCategory",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    entry_type = models.CharField(max_length=30, choices=EntryType.choices) # The type of this entry (CREDIT, DIRECT_RECEIPT, etc.)
    description = models.CharField(max_length=255, blank=True) # Aditional description for this entry, if needed. 

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # The document from which this entry was imported, if applicable. This field is optional and can be null.
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