from core.shifts_dict import STAFFING_HOURS


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

def staffing_filter(balance, filter_type):
    print("Applying filter:", filter_type, "to balance")
    return balance