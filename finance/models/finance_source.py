from django.db import models


class FinanceSource(models.Model):
    name = models.CharField(max_length=100)
    pays_directly_to_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)