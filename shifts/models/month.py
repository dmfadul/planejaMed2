from django.db import models
from core.models import User


class Month(models.Model):
    year = models.IntegerField()
    number = models.IntegerField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='month_leader')
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)


# class Center(models.Model):
#     name = models.CharField(max_length=100)
#     abbreviation = models.CharField(max_length=5)
#     hospital = models.CharField(max_length=100, default='Evangélico')
#     is_active = models.BooleanField(default=True)


# class Holiday(models.Model):
#     month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
#     day = models.IntegerField()


# class AbstractShift(models.Model):
#     """Class will be inherited by shift and BaseShift."""
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     time_start = models.TimeField()
#     time_end = models.TimeField()

#     class Meta:
#         abstract = True


# class TemplateShift(AbstractShift):
#     center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
#     weekday = models.IntegerField()
#     index = models.IntegerField()


# class Shift(AbstractShift):
#     center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
#     month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
#     day = models.IntegerField()
