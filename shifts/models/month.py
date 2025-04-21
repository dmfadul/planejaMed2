from django.db import models
from core.models import User


class Month(models.Model):
    year = models.IntegerField()
    number = models.IntegerField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='month_leader')
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)


# class Holiday(models.Model):
#     month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
#     day = models.IntegerField()
