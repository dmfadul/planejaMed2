from django.contrib import admin
from .models import Month, Holiday, Center
from .models import Shift, TemplateShift 
from .models import ShiftSnapshot


admin.site.register(Month)
admin.site.register(Holiday)
admin.site.register(Center)
admin.site.register(Shift)
admin.site.register(TemplateShift)
admin.site.register(ShiftSnapshot)
