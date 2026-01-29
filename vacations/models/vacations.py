from django.db import models, transaction
from core.models import User


class Vacation(models.Model):
    class VacationType(models.TextChoices):
        REGULAR = 'regular', 'Regular'
        SICK = 'sick', 'Sick Leave'

    class VacationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        OVERRIDDEN = 'overridden', 'Overridden'

    class paymentStatus(models.TextChoices):
        PAID = 'paid', 'Paid'
        UNPAID = 'unpaid', 'Unpaid'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacations')
    start_date = models.DateField()
    end_date = models.DateField()
    vacation_type = models.CharField(max_length=20, choices=VacationType.choices, default=VacationType.REGULAR)
    status = models.CharField(max_length=20, choices=VacationStatus.choices, default=VacationStatus.PENDING)
    

    def __str__(self):
        return f"{self.user.name} - {self.vacation_type} from {self.start_date} to {self.end_date} ({self.status})"
    

    @classmethod
    def overlaps_qs(cls, *, user, start_date, end_date, exclude_pk=None):
        """
        Overlap rule (inclusive): [start_date, end_date] overlaps if:
        existing.start_date <= end_date AND existing.end_date >= start_date
        """
        qs = cls.objects.filter(user=user, start_date__lte=end_date, end_date__gte=start_date)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        return qs

    @classmethod
    def create_vacation(cls, *, user, start_date, end_date, vacation_type):
        # Basic validation
        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date.")

        with transaction.atomic():
            # Lock potentially-conflicting rows to avoid race conditions
            overlapping = (
                cls.overlaps_qs(user=user, start_date=start_date, end_date=end_date)
                .select_for_update()
            )

            if overlapping.exists():
                return -1  # Indicate conflict

            vacation = cls.objects.create(
                user=user,
                start_date=start_date,
                end_date=end_date,
                vacation_type=vacation_type,
                status=cls.VacationStatus.APPROVED,
            )
            return vacation

    @property
    def phase(self):
        """Determine the current phase of the vacation. Scheduled, in progress, completed, etc."""
        # TODO: Implement phase determination logic
        pass

    @property
    def duration_days(self):
        from core.constants import VACATION_RULES
        """
        Calculate the total number of days for the vacation.
        Enforce minimum days per request and other rules.
        """
        
        actual_duration = (self.end_date - self.start_date).days + 1
        min_duration = VACATION_RULES.get('min_days_per_request', 0)
        sick_leave_to_vacation = VACATION_RULES.get('sick_leave_to_vacation', 0) # max number of sick days that are deducted from vacation days

        if self.vacation_type == Vacation.VacationType.SICK and actual_duration > sick_leave_to_vacation:
            return sick_leave_to_vacation

        if self.vacation_type == Vacation.VacationType.REGULAR and actual_duration < min_duration:
            return min_duration

        return actual_duration
