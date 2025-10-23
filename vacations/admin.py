from django.contrib import admin
from .models import Vacation, ComplianceHistory

# Register your models here.
admin.site.register(Vacation)
admin.site.register(ComplianceHistory)
