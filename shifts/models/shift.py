from django.db import models
from shifts.models.month import Month
from shifts.models.shift_abstract import AbstractShift
   

class Shift(AbstractShift):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
    day = models.IntegerField()
