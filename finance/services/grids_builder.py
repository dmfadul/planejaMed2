from decimal import Decimal
from core.models import User
from shifts.models import Shift
from collections import defaultdict
from core.constants import STR_DAY, END_DAY
from django.db.models.functions import Collate
from core.db.sqlite_collations import COLLATION_NAME
from finance.models import FinanceConstant, FinanceEntry
from core.constants import ROUTINE_RATE, OVERTIME_RATE




def build_user_monthly_hours_payload(user, month):
    """
    Returns monthly routine/overtime hours grouped by center
    for the logged-in user only. Used for the "My payment" page.
    """

    shifts = (
        Shift.objects
        .filter(user=user, month=month)
        .select_related("center")
    )

    centers = defaultdict(lambda: {
        "routine_hours": 0,
        "overtime_hours": 0,
    })

    for shift in shifts:
        counts = shift.get_overtime_count()
        center_abbreviation = shift.center.abbreviation

        centers[center_abbreviation]["routine_hours"] += counts.get("normal", 0)
        centers[center_abbreviation]["overtime_hours"] += counts.get("overtime", 0)

    centers_payload = []
    for abbreviation, hours in centers.items():
        routine = hours["routine_hours"]
        overtime = hours["overtime_hours"]

        centers_payload.append({
            "abbreviation": abbreviation,
            "routine_hours": routine,
            "overtime_hours": overtime,
            "total_hours": routine + overtime,
        })

    centers_payload.sort(key=lambda x: x["abbreviation"])

    return {
        "doctor": user.name,
        "month": f"{month.name}/{month.year}",
        "rates": {
            "routine": ROUTINE_RATE,
            "overtime": OVERTIME_RATE,
        },
        "centers": centers_payload,
    }

