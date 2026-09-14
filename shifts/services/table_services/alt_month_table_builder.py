from datetime import date, timedelta
from shifts.models import Shift
from .alt_table_builder import (
    shift_occupies_period,
    create_block,
)

from core.constants import (
    DIAS_SEMANA,
    NUMBER_OF_ROWS_PER_CENTER,
    STR_DAY,
    END_DAY,
)


def get_month_table_dates(month):
    """
    Return all dates represented by the schedule.

    Example, if STR_DAY = 26 and END_DAY = 25:

        26/previous month, 27/previous month, ...
        1/current month, 2/current month, ... 25/current month
    """
    previous_month, previous_year = month.prv_number_year()

    start_date = date(previous_year, previous_month, STR_DAY)
    end_date = date(month.year, month.number, END_DAY)

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def split_into_weeks(dates):
    """Split the dates into groups of at most seven days."""
    return [
        dates[index:index + 7]
        for index in range(0, len(dates), 7)
    ]


def gen_month_header_row(week_dates):
    """
    Generate the weekday-name header for one week.

    datetime.weekday():
        Monday = 0
        Tuesday = 1
        ...
        Sunday = 6

    This assumes DIAS_SEMANA follows the same order.
    """
    return [
        {
            "label": DIAS_SEMANA[current_date.weekday()],
        }
        for current_date in week_dates
    ]


def gen_month_subheader_row(week_dates):
    """Generate the numeric day header for one week."""
    return [
        {
            "label": DIAS_SEMANA[current_date.weekday()],
            "number": current_date.day,
            "is_weekend": current_date.weekday() in (5, 6),
        }
        for current_date in week_dates
    ]

def fill_month_block(block, shifts, week_dates):
    if not block:
        return block

    period = block[0]["period"]

    date_column_map = {
        current_date: column_index
        for column_index, current_date in enumerate(week_dates)
    }

    for shift in shifts:
        if not shift_occupies_period(shift, period):
            continue

        shift_date = shift.date.date()

        column_index = date_column_map.get(shift_date)

        if column_index is None:
            continue

        center_code = shift.center.abbreviation

        available_row = next(
            (
                row
                for row in block
                if row["days"][column_index]["code"] == center_code
                and not row["days"][column_index]["name"]
            ),
            None,
        )

        if available_row is None:
            available_row = add_extra_row(
                block=block,
                period=period,
                center_code=center_code,
            )

        available_row["days"][column_index]["name"] = shift.user.name

    return block


def add_extra_row(block, period, center_code, number_of_days=None):
    if number_of_days is None:
        number_of_days = len(block[0]["days"]) if block else 7

    new_row = {
        "counter": 0,
        "period": period,
        "days": [
            {"code": center_code, "name": ""}
            for _ in range(number_of_days)
        ],
    }

    center_row_indexes = [
        index
        for index, row in enumerate(block)
        if row["days"][0]["code"] == center_code
    ]

    if center_row_indexes:
        insertion_index = center_row_indexes[-1] + 1
        block.insert(insertion_index, new_row)
    else:
        block.append(new_row)

    for counter, row in enumerate(block, start=1):
        row["counter"] = counter

    return new_row

def build_alt_month_table_data(month):
    shifts = list(
        Shift.objects
        .filter(month=month)
        .select_related("user", "center")
        .order_by(
            "day",
            "center__abbreviation",
            "start_time",
            "user__name",
        )
    )

    table_dates = get_month_table_dates(month)
    date_weeks = split_into_weeks(table_dates)

    weeks = []

    for week_index, week_dates in enumerate(date_weeks, start=1):
        week_date_set = set(week_dates)

        week_shifts = [
            shift
            for shift in shifts
            if shift.date.date() in week_date_set
        ]

        schedule_rows = []

        for period, period_dict in NUMBER_OF_ROWS_PER_CENTER.items():
            block = create_block(
                period=period,
                period_dict=period_dict,
                number_of_days=len(week_dates),
            )

            fill_month_block(
                block=block,
                shifts=week_shifts,
                week_dates=week_dates,
            )

            schedule_rows.extend(block)

        weeks.append({
            "index": week_index,
            "header": gen_month_header_row(week_dates),
            "subheader": gen_month_subheader_row(week_dates),
            "schedule_rows": schedule_rows,
        })

    return {
        "hospital_name": "HOSPITAL UNIVERSITÁRIO EVANGÉLICO MACKENZIE",
        "group_name": "GRUPO DE ANESTESIA MACKENZIE - CCG",
        "month": month,
        "weeks": weeks,
    }