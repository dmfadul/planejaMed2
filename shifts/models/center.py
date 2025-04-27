from django.db import models
from core.models import User


class Center(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5, unique=True)
    hospital = models.CharField(max_length=100, default='Evangélico')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.abbreviation
    