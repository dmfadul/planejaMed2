from django.conf import settings
from django.db import models


class HospitalFinancialBatch(models.Model):
    class BatchType(models.TextChoices):
        ORIGINAL = "original", "Original hospital file"
        COOP = "coop", "Cooperative version"

    month = models.ForeignKey(
        "shifts.Month",
        on_delete=models.PROTECT,
        related_name="hospital_financial_batches",
    )

    batch_type = models.CharField(
        max_length=20,
        choices=BatchType.choices,
    )

    version = models.PositiveIntegerField(default=1)

    source_batch = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="derived_batches",
        help_text="Original hospital batch from which this version was generated.",
    )

    uploaded_document = models.ForeignKey(
        "finance.UploadedDocument",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="financial_batches",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="created_financial_batches",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["month", "batch_type", "version"],
                name="unique_financial_batch_version",
            ),
        ]
        ordering = ["-month__year", "-month__number", "batch_type", "-version"]

    def __str__(self):
        return (
            f"{self.month} - "
            f"{self.get_batch_type_display()} v{self.version}"
        )
    

class HospitalFinancialEntry(models.Model):
    batch = models.ForeignKey(
        HospitalFinancialBatch,
        on_delete=models.CASCADE,
        related_name="entries",
    )

    health_plan_name = models.CharField(  # C/2
        "Nome Convênio",
        max_length=255,
        blank=True,
    )

    procedure_description = models.CharField( # D/3
        "Descrição Procedimento",
        max_length=500,
        blank=True,
    )

    provider_name = models.CharField( # E/4
        "Nome Prestador",
        max_length=255,
        blank=True,
    )

    transfer_description = models.CharField( # F/5
        "Descrição Repasse",
        max_length=500,
        blank=True,
    )

    amount = models.DecimalField( # H/7
        "Valor",
        max_digits=12,
        decimal_places=2,
    )

    source_entry = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="derived_entries",
        help_text="Original hospital entry corresponding to this cooperative entry.",
    )

    row_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Original row number in the imported spreadsheet.",
    )

    class Meta:
        ordering = ["row_number", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "row_number"],
                condition=models.Q(row_number__isnull=False),
                name="unique_row_number_per_financial_batch",
            ),
        ]

    def __str__(self):
        return f"{self.provider_name} - {self.amount}"