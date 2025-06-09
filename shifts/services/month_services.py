# shifts/services/month_services.py

from datetime import datetime, timedelta

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

    for i, t in enumerate(templates):
        day_offset_curr = (t.weekday - first_wday + 7) % 7
        day_offset_prv = (t.weekday - prv_first_wday + 7) % 7

        curr_date = first_day + timedelta(days=day_offset_curr) + timedelta(weeks=t.index - 1)
        prv_date = prv_first_day + timedelta(days=day_offset_prv) + timedelta(weeks=t.index - 1)
        if "Felype" in t.user.name and (curr_date.day == 4 or prv_date.day == 4):
            print(curr_date, prv_date, t.user, t.center, t.start_time, t.end_time)
        # if curr_date.month == prv_date.month:

        # for target_date in [curr_date, prv_date]:
        #     if month.start_date <= target_date <= month.end_date:
        #         Shift.objects.create(
        #             user=t.user,
        #             center=t.center,
        #             month=month,
        #             day=target_date.day,
        #             start_time=t.start_time,
        #             end_time=t.end_time
        #         )

    print(f"Month {month} populated.")
