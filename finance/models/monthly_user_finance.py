from django.db import models


class MonthlyUserFinance(models.Model):
    month = models.ForeignKey("shifts.Month", on_delete=models.CASCADE)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)

    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    direct_received_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adjustments_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    final_amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("month", "user")