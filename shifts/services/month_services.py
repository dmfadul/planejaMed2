from dataclasses import dataclass
from django.db import transaction
from datetime import date, datetime, time, timedelta


@dataclass
class PlannedShift:
    user: object
    center: object
    month: object
    date: date
    start_time: time
    end_time: time


def get_planned_shifts(month, user=None):
    from shifts.models import TemplateShift

    year, num = month.year, month.number

    first_day = datetime(year, num, 1)
    first_wday = first_day.weekday()

    previous_year = month.start_date.year
    previous_month = month.start_date.month

    previous_first_day = datetime(previous_year, previous_month, 1)
    previous_first_wday = previous_first_day.weekday()

    templates = TemplateShift.objects.filter(user__is_active=True, user__is_invisible=False)
    
    if user is not None:
        templates = templates.filter(user=user)
    
    planned_shifts = []

    for template in templates:
        current_offset = (template.weekday - first_wday + 7) % 7
        previous_offset = (template.weekday - previous_first_wday + 7) % 7

        current_date = (
            first_day
            + timedelta(days=current_offset)
            + timedelta(weeks=template.index - 1)
        )

        previous_date = (
            previous_first_day
            + timedelta(days=previous_offset)
            + timedelta(weeks=template.index - 1)
        )
        
        target_dates = []

        if month.start_date <= previous_date <= month.break_date:
            target_dates.append(previous_date)

        if month.start_date <= current_date <= month.end_date:
            target_dates.append(current_date)

        for target_date in target_dates:
            planned_shifts.append(
                PlannedShift(
                    user=template.user,
                    center=template.center,
                    month=month,
                    date=target_date.date(),
                    start_time=template.start_time,
                    end_time=template.end_time
                )
            )

    return planned_shifts


def populate_month(month):
    from shifts.models import Shift

    print(f"Populating month {month}...")

    planned_shifts = get_planned_shifts(month)

    shifts_to_create = [
        Shift(
            user=planned_shift.user,
            center=planned_shift.center,
            month=month,
            day=planned_shift.date.day,
            start_time=planned_shift.start_time,
            end_time=planned_shift.end_time
        )
        for planned_shift in planned_shifts
    ]
    
    with transaction.atomic():
        Shift.objects.bulk_create(shifts_to_create)

    print(f"Month {month} populated with {len(shifts_to_create)} shifts.")
