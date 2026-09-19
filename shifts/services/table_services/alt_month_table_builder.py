from datetime import date, timedelta

from shifts.models import Shift
from .alt_table_builder import shift_occupies_period

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
    """
    Split dates into Saturday-to-Friday weeks.

    Empty columns before the first date and after the final date
    are represented by None.
    """
    if not dates:
        return []

    saturday_index = 5

    leading_empty_columns = (
        dates[0].weekday() - saturday_index
    ) % 7

    padded_dates = [None] * leading_empty_columns + dates

    trailing_empty_columns = (-len(padded_dates)) % 7
    padded_dates.extend([None] * trailing_empty_columns)

    return [
        padded_dates[index:index + 7]
        for index in range(0, len(padded_dates), 7)
    ]


def gen_month_header_row():
    """
    Generate the weekday-name header from Saturday to Friday.

    datetime.weekday():
        Monday = 0
        Tuesday = 1
        ...
        Saturday = 5
        Sunday = 6
    """
    weekday_indexes = [5, 6, 0, 1, 2, 3, 4]

    return [
        {
            "label": DIAS_SEMANA[weekday_index],
        }
        for weekday_index in weekday_indexes
    ]


def gen_month_subheader_row(week_dates):
    """
    Generate the numeric day header.

    Empty positions are used to complete Saturday-to-Friday weeks.
    """
    return [
        {
            "label": (
                DIAS_SEMANA[current_date.weekday()]
                if current_date is not None
                else ""
            ),
            "number": (
                current_date.day
                if current_date is not None
                else ""
            ),
            "is_weekend": (
                current_date.weekday() in (5, 6)
                if current_date is not None
                else False
            ),
            "is_empty": current_date is None,
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
        if current_date is not None
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


def create_block(period, period_dict, number_of_days=7, exclude_eco=False):
    block = []
    counter = 1

    for center_abbr, num_rows in period_dict.items():
        if exclude_eco and center_abbr == "ECO":
            continue
        for _ in range(num_rows):
            row = {
                "counter": counter,
                "period": period,
                "days": [
                    {
                        "code": center_abbr,
                        "name": "",
                    }
                    for _ in range(number_of_days)
                ],
            }

            block.append(row)
            counter += 1

    return block


def add_extra_row(
    block,
    period,
    center_code,
    number_of_days=None,
):
    if number_of_days is None:
        number_of_days = len(block[0]["days"]) if block else 7

    new_row = {
        "counter": 0,
        "period": period,
        "days": [
            {
                "code": center_code,
                "name": "",
            }
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


def build_alt_month_table_data(month, exclude_eco=False):
    shifts_queryset = (
        Shift.objects
        .filter(
            month=month,
            user__is_active=True,
            user__is_invisible=False,
        )
        .select_related("user", "center")
    )

    if exclude_eco:
        shifts_queryset = shifts_queryset.exclude(
            center__abbreviation="ECO"
        )

    shifts = list(
        shifts_queryset.order_by(
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
        week_date_set = {
            current_date
            for current_date in week_dates
            if current_date is not None
        }

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
                number_of_days=7,
                exclude_eco=exclude_eco
            )

            fill_month_block(
                block=block,
                shifts=week_shifts,
                week_dates=week_dates,
            )

            schedule_rows.extend(block)

        weeks.append({
            "index": week_index,
            "header": gen_month_header_row(),
            "subheader": gen_month_subheader_row(week_dates),
            "schedule_rows": schedule_rows,
        })

    return {
        "hospital_name": (
            "HOSPITAL UNIVERSITÁRIO EVANGÉLICO MACKENZIE"
        ),
        "group_name": "GRUPO DE ANESTESIA MACKENZIE - CCG",
        "month": month,
        "weeks": weeks,
    }