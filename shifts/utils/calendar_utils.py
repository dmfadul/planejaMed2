from datetime import timedelta

def gen_date_row(start_date, end_date):
    dates = []
    while start_date <= end_date:
        dates.append(start_date)
        start_date += timedelta(days=1)
    return dates

def gen_calendar_table(start_date, end_date):
    cal_table = []
    week = [""] * 7
    current_date = start_date

    while current_date <= end_date:
        weekday = current_date.weekday()
        week[weekday] = current_date.day
        if weekday == 6:
            cal_table.append(week)
            week = [""] * 7
        current_date += timedelta(days=1)

    if any(week):
        cal_table.append(week)
    return cal_table
