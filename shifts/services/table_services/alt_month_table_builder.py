from datetime import date, timedelta
from shifts.models import Shift

from core.constants import (
    SHIFTS_MAP,
    DIAS_SEMANA,
    NUMBER_OF_ROWS_PER_CENTER,
    STR_DAY,
    END_DAY,
)


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
