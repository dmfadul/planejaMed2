from django.db import models


class FinanceConstant(models.Model):
    month = models.ForeignKey("shifts.Month", on_delete=models.CASCADE)

    code = models.SlugField(max_length=50)
    label = models.CharField(max_length=100)

    value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["month", "code"]
        ordering = ["order", "label"]
