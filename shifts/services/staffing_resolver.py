from core.shifts_dict import STAFFING_HOURS
from django.utils import timezone


def get_day_type(weekday_int: int, holiday: bool) -> str:
    if holiday:
        return "holiday"
    if weekday_int == 5:
        return "saturday"
    if weekday_int == 6:
        return "sunday"
    return "weekday"


def get_staffing_hours(center, weekday_int, holiday) -> dict[str, int]:
    staffing_hours = STAFFING_HOURS
    day_type = get_day_type(weekday_int, holiday)

    center_data = staffing_hours.get(center.abbreviation)
    if center_data is None:
        raise KeyError(f"Unknown center: {center}")

    if "all" in center_data:
        return center_data["all"]
    
    if holiday and "holiday" in center_data:
        return center_data["holiday"]
    
    day_data = center_data.get(day_type)

    if day_data is None:
        return {
            "morning": 0,
            "afternoon": 0,
            "night": 0,
        }

    return day_data


def remove_past_days(balance):
    from core.constants import STR_DAY, END_DAY

    today = timezone.localdate().day
    if STR_DAY <= today <= 31:
        cleaned_balance = {d: s for d, s in balance.items() if int(d.split("/")[0]) >= today or 1 <= d <= END_DAY}
    else:
        cleaned_balance = {d: s for d, s in balance.items() if not(31 >= int(d.split("/")[0]) >= STR_DAY)}
        cleaned_balance = {d: s for d, s in cleaned_balance.items() if int(d.split("/")[0]) >= today}

    return cleaned_balance


def staffing_filter(balance, filter_type):
    if filter_type == "understaffed":
        filtered = {
            day: {k: v for k, v in shifts.items() if v < 0}
            for day, shifts in balance.items()
            if any(v < 0 for v in shifts.values())
        }
    elif filter_type == "overstaffed":
        filtered = {
            day: {k: v for k, v in shifts.items() if v > 0}
            for day, shifts in balance.items()
            if any(v > 0 for v in shifts.values())
        }
    elif filter_type == "removeZeroes":
        filtered = {
            day: {k: v for k, v in shifts.items() if v != 0}
            for day, shifts in balance.items()
            if any(v != 0 for v in shifts.values())
        }
    else:
        filtered = balance
    
    filtered = remove_past_days(filtered)
    return filtered