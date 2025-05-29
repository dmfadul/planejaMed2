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
    

    @classmethod
    def take_snapshot(cls, month, shift_type):
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
        else:
            shifts = Shift.objects.filter(month=month)
            snapshots = [
                cls(
                    user=shift.user,
                    center=shift.center,
                    month=month,
                    start_time=shift.start_time,
                    end_time=shift.end_time,
                    day=shift.day,
                    type=shift_type
                )
                for shift in shifts
            ]
        cls.objects.bulk_create(snapshots)
        return True


    @classmethod
    def recover_snapshot(cls, month, shift_type, organize_by='user'):
        pass
        # if shift_type == ShiftType.BASE:
        #     tshifts = TemplateShift.objects.all()
        #     snapshots = [
        #         cls(
        #             user=shift.user,
        #             center=shift.center,
        #             month=month,
        #             start_time=shift.start_time,
        #             end_time=shift.end_time,
        #             weekday=shift.weekday,
        #             index=shift.index,
        #             type=ShiftType.BASE
        #         )
        #         for shift in tshifts
        #     ]
        # else:
        #     shifts = Shift.objects.filter(month=month)
        #     snapshots = [
        #         cls(
        #             user=shift.user,
        #             center=shift.center,
        #             month=month,
        #             start_time=shift.start_time,
        #             end_time=shift.end_time,
        #             day=shift.day,
        #             type=shift_type
        #         )
        #         for shift in shifts
        #     ]
        # cls.objects.bulk_create(snapshots)
        # return True
