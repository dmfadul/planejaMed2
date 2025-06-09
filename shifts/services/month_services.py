from datetime import datetime, timedelta
from core.constants import END_DAY


def populate_month(month):
    from shifts.models import Shift, TemplateShift
    print(f"Populating month {month}...")

    year, num = month.year, month.number
    first_day = datetime(year, num, 1)
    last_day = datetime(year, num, END_DAY)
    first_wday = first_day.weekday()

    prv_year, prv_month = month.start_date.year, month.start_date.month
    prv_first_day = datetime(prv_year, prv_month, 1)
    prv_first_wday = prv_first_day.weekday()

    templates = TemplateShift.objects.filter(user__is_active=True)

    for i, t in enumerate(templates):
        day_offset_curr = (t.weekday - first_wday + 7) % 7
        day_offset_prv = (t.weekday - prv_first_wday + 7) % 7

        curr_date = first_day + timedelta(days=day_offset_curr) + timedelta(weeks=t.index - 1)
        prv_date = prv_first_day + timedelta(days=day_offset_prv) + timedelta(weeks=t.index - 1)
        if curr_date > last_day:
            continue

        for target_date in [curr_date, prv_date]:
            if month.start_date <= target_date <= month.end_date:
                Shift.objects.create(
                    user=t.user,
                    center=t.center,
                    month=month,
                    day=target_date.day,
                    start_time=t.start_time,
                    end_time=t.end_time
                )

    print(f"Month {month} populated.")
