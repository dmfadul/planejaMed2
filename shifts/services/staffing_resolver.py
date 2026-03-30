from core.shifts_dict import STAFFING_HOURS


def get_day_type(weekday_int: int, holiday: bool) -> str:
    if holiday:
        return "holiday"
    if weekday_int == 5:
        return "saturday"
    if weekday_int == 6:
        return "sunday"
    return "weekday"


def get_staffing_hours(center: object, weekday_int: int, holiday: bool) -> int:
    staffing_hours = STAFFING_HOURS
    day_type = get_day_type(weekday_int, holiday)

    center_data = staffing_hours.get(center.abbreviation)
    if center_data is None:
        raise KeyError(f"Unknown center: {center}")

    # exact match first, then fallback to "all"
    day_data = center_data.get(day_type) or center_data.get("all")
    if day_data is None:
        raise KeyError(
            f"No staffing rule found for center={center!r}, day_type={day_type!r}"
        )

    return day_data