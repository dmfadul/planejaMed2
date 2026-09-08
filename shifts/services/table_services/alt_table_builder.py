from core.models import User
from shifts.models import Center, Month, Shift, TemplateShift
from core.constants import SHIFTS_MAP, DIAS_SEMANA, NUMBER_OF_ROWS_PER_CENTER


def get_interval_hours(start, end):
    """
    Return the hours occupied by a shift.

    Examples:
        7–13  -> {7, 8, 9, 10, 11, 12}
        19–1  -> {19, 20, 21, 22, 23, 0}
        7–7   -> all 24 hours
    """
    if start == end:
        return set(range(24))

    hours = set()
    current = start

    while current != end:
        hours.add(current)
        current = (current + 1) % 24

    return hours


def shift_occupies_period(shift, period):
    period_start, period_end = SHIFTS_MAP[period]

    shift_hours = get_interval_hours(
        shift.start_time,
        shift.end_time,
    )
    period_hours = get_interval_hours(
        period_start,
        period_end,
    )

    return not shift_hours.isdisjoint(period_hours)

def fill_block(block, shifts):
    if not block:
        return block

    period = block[0]["period"]

    for shift in shifts:
        if not shift_occupies_period(shift, period):
            continue

        center_code = shift.center.abbreviation
        weekday = shift.weekday

        # Find the first available row belonging to this center.
        available_row = next(
            (
                row
                for row in block
                if row["days"][weekday]["code"] == center_code
                and not row["days"][weekday]["name"]
            ),
            None,
        )

        if available_row is None:
            raise ValueError(
                f"Not enough rows for center {center_code}, "
                f"period {period}, weekday {weekday}."
            )

        available_row["days"][weekday]["name"] = (
            shift.user.name
        )

    return block


def create_block(period, period_dict):
    weekdays = range(7)
    block = []
    counter = 1

    for center_abbr, num_rows in period_dict.items():
        for _ in range(num_rows):
            row = {
                "counter": counter,
                "period": period,
                "days": [
                    {"code": center_abbr, "name": ""}
                    for _ in weekdays
                ],
            }

            block.append(row)
            counter += 1

    return block


def gen_subheader_row(week_index):
    subheader = []

    for day_index in range(7):
        subheader.append({
            "label": DIAS_SEMANA[day_index],
            "number": week_index,
            "is_weekend": day_index in [5, 6],
        })

    return subheader


def gen_header_row():
    header = []
    for i in range(5, 12):
        day_index = i % 7
        header.append({"label": DIAS_SEMANA[day_index]})
    return header


def build_alt_template_table_data():
    shifts = list(
        TemplateShift.objects
        .filter(index__range=(1, 5))
        .select_related("user", "center")
        .order_by(
            "index",
            "weekday",
            "center__abbreviation",
            "start_time",
            "user__name",
        )
    )

    weeks = []
    for week_index in range(1, 6):
        week_shifts = [
            shift
            for shift in shifts
            if shift.index == week_index
        ]

        schedule_rows = []

        for period, period_dict in NUMBER_OF_ROWS_PER_CENTER.items():
            block = create_block(period, period_dict)
            fill_block(block, week_shifts)
            schedule_rows.extend(block)

        weeks.append({
            "index": week_index,
            "header": gen_header_row(),
            "subheader": gen_subheader_row(week_index),
            "schedule_rows": schedule_rows,
        })

    return {
        "hospital_name": "HOSPITAL UNIVERSITÁRIO EVANGÉLICO MACKENZIE",
        "group_name": "GRUPO DE ANESTESIA MACKENZIE - CCG",
        "weeks": weeks,
    }


def build_alt_table_data():
    return build_alt_template_table_data()
