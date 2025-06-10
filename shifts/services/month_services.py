from datetime import datetime, timedelta
from django.db import transaction


def populate_month(month):
    from shifts.models import Shift, TemplateShift
    print(f"Populating month {month}...")

    year, num = month.year, month.number
    first_day = datetime(year, num, 1)
    first_wday = first_day.weekday()

    prv_year, prv_month = month.start_date.year, month.start_date.month
    prv_first_day = datetime(prv_year, prv_month, 1)
    prv_first_wday = prv_first_day.weekday()

    templates = TemplateShift.objects.filter(user__is_active=True)
    shifts_to_create = []

    for t in templates:
        day_offset_curr = (t.weekday - first_wday + 7) % 7
        day_offset_prv = (t.weekday - prv_first_wday + 7) % 7

        curr_date = first_day + timedelta(days=day_offset_curr) + timedelta(weeks=t.index - 1)
        prv_date = prv_first_day + timedelta(days=day_offset_prv) + timedelta(weeks=t.index - 1)
        
        targets = []
        if month.start_date <= prv_date <= month.break_date:
            targets.append(prv_date)
        if month.start_date <= curr_date <= month.end_date:
            targets.append(curr_date)

        for target_date in targets:
            shifts_to_create.append(Shift(
                user=t.user,
                center=t.center,
                month=month,
                day=target_date.day,
                start_time=t.start_time,
                end_time=t.end_time
            ))
    with transaction.atomic():
        Shift.objects.bulk_create(shifts_to_create)

    print(f"Month {month} populated with {len(shifts_to_create)} shifts.")
