from django.db import models
from core.models import User
from shifts.models import Month, Center, Shift, TemplateShift


class ShiftType(models.TextChoices):
    BASE = 'base', 'Base'
    ORIGINAL = 'original', 'Original'
    REALIZED = 'realized', 'Realized'


class ShiftSnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='shiftsnapshots')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shiftsnapshots')
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    weekday = models.IntegerField(null=True, blank=True)
    index = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=10, choices=ShiftType.choices)

    class Meta:
        indexes = [
            models.Index(fields=['center', 'month', 'type']),
        ]

    def __str__(self):
        return f"{self.type} - {self.center.abbreviation} - {self.user.abbr_name}"
    

    @classmethod
    def take_snapshot(cls, month, shift_type):
        cls.delete_snapshot(month, shift_type)

        if shift_type == ShiftType.BASE:
            tshifts = TemplateShift.objects.all()
            snapshots = [
                cls(
                    user=shift.user,
                    center=shift.center,
                    month=month,
                    start_time=shift.start_time,
                    end_time=shift.end_time,
                    weekday=shift.weekday,
                    index=shift.index,
                    type=ShiftType.BASE
                )
                for shift in tshifts
            ]
            cls.objects.bulk_create(snapshots)
        return True

    @classmethod
    def delete_snapshot(cls, month, shift_type):
        cls.objects.filter(month=month, type=shift_type).delete()
        return True

    @classmethod
    def load_snapshot(cls, month, shift_type, organize_by='user'):
        return cls.objects.filter(month=month, type=shift_type).order_by(organize_by)