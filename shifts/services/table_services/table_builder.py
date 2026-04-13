from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA, BONUS_RULES, SHIFTS_MAP
from .table_utils import translate_to_table, gen_headers
from shifts.models import Center, Month, Shift, TemplateShift
from shifts.models import TemplateShift as TS
from core.models import User
from ..staffing_resolver import get_staffing_hours, staffing_filter
from collections import defaultdict


def build_table_data(table_type, template, center=None, doctor=None, month=None, filter_type=None):
    table_data = {
        "header1": None,
        "header2": None,
        "center": None,
        "month": 0,
        "year": 0,
        "table_type": table_type,
        "template": template,
        "shift_codes": ["-"] + SHIFT_CODES,
        "hour_range": [f"{x:02d}:00" for x in HOUR_RANGE],
        "hour_values": {f"{x:02d}:00": x for x in HOUR_RANGE},
        "show_back_button": 0,
        "holidays": [],
    }

    if center:
        table_data["center"] = center.abbreviation
    
    if template == "basetable":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        return build_basetable(center, table_data, template=template)

    if template == "month_table":
        table_data["header1"], table_data["header2"] = gen_headers(template, month)
        table_data["month"] = month.name.upper()
        table_data["month_number"] = month.number
        table_data["year"] = month.year

        return build_basetable(center, table_data, template=template, month=month)
    
    if template == "doctor_basetable":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["show_back_button"] = 1
        return build_doctor_table(doctor, center, table_data)
    
    if template == "sum_days_base":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["show_back_button"] = 1
        return build_sumtable(center, table_data, template=template)
    
    if template == "sum_days_month":
        table_data["header1"], table_data["header2"] = gen_headers(template, month)
        table_data["month"] = month.name.upper()
        table_data["month_number"] = month.number
        table_data["year"] = month.year
        table_data["show_back_button"] = 1
        return build_sumtable(center, table_data, template=template, month=month)
    
    if template == "sum_doctors_base":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["center"] = ""
        return build_doctors_sumtable(table_data, template)
    
    if template == "sum_doctors_month":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["center"] = ""
        return build_doctors_sumtable(table_data, template=template, month=month)

    if template == "balance":
        table_data["header1"], table_data["header2"] = [], []
        table_data["center"] = ""
        table_data["month"] = month.name.upper()
        table_data["year"] = month.year

        return build_balance_table(table_data, month=month, filter_type=filter_type)


def build_doctors_sumtable(table_data, template, month=None):
    bonus_hours = BONUS_RULES["bonus_hours"]
    bonus_perc = BONUS_RULES["bonus_perc"]

    doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    table_data["doctors"] = []
    for doctor in doctors:
        shifts = {}
        if template == "sum_doctors_base":
            all_shifts = TS.objects.filter(user=doctor).all()
        else:
            all_shifts = Shift.objects.filter(user=doctor, month=month).all()

        total_overtime, total_normal = 0, 0
        for s in all_shifts:
            cell_id_over = f"cell-{doctor.crm}-{s.center.abbreviation}-overtime"
            cell_id_norm = f"cell-{doctor.crm}-{s.center.abbreviation}-normal"

            if cell_id_over not in shifts:
                shifts[cell_id_over] = 0
            if cell_id_norm not in shifts:
                shifts[cell_id_norm] = 0

            hours_dict = s.get_overtime_count()
            
            overtime = hours_dict["overtime"]
            normal = hours_dict["normal"]

            shifts[cell_id_over] += overtime
            shifts[cell_id_norm] += normal

            total_overtime += overtime
            total_normal += normal

        # add zeroes for missing centers
        for center in Center.objects.filter(is_active=True).all():
            cell_id_over = f"cell-{doctor.crm}-{center.abbreviation}-overtime"
            cell_id_norm = f"cell-{doctor.crm}-{center.abbreviation}-normal"

            if cell_id_over not in shifts:
                shifts[cell_id_over] = 0
            if cell_id_norm not in shifts:
                shifts[cell_id_norm] = 0
        
        # add totals
        cell_id_tot_over = f"cell-{doctor.crm}-TOTAL-overtime"
        cell_id_tot_norm = f"cell-{doctor.crm}-TOTAL-normal"
        cell_id_tot_adc = f"cell-{doctor.crm}-TOTAL"
        
        shifts[cell_id_tot_over] = total_overtime
        shifts[cell_id_tot_norm] = total_normal
        adc = round(total_overtime * bonus_perc, 0) if total_overtime >= bonus_hours else 0
        shifts[cell_id_tot_adc] = adc

        table_data["doctors"].append({"name": doctor.name,
                                      "abbr_name": doctor.abbr_name,
                                      "crm": doctor.crm,
                                      "shifts": shifts,})

    return table_data


def build_balance_table(table_data, month, filter_type=None):
    PERIODS = ("morning", "afternoon", "night")

    def empty_periods():
        return {
            "morning": 0,
            "afternoon": 0,
            "night": 0,
        }
    
    center_data = {}

    centers = Center.objects.filter(is_active=True).all()
    holiday_days = set(month.holidays.values_list("day", flat=True))

    for center in centers:
        shifts = Shift.objects.filter(
            center=center,
            month=month,
            user__is_invisible=False
        )
        
        # day -> worked hours grouped by period
        hours_by_day = defaultdict(empty_periods)

        # 1. Sum actual worked hours for each day
        for shift in shifts:
            day = shift.day
            shift_hours = shift.get_hours_count()

            for period in PERIODS:
                hours_by_day[day][period] += shift_hours.get(period, 0)

        # 2. Compare actual hours with required staffing hours
        balance_by_day = {}
        for month_date in month.days:
            day = month_date.day
            weekday_int = month_date.weekday()
            holiday = day in holiday_days

            staffing_hours = get_staffing_hours(
                center=center,
                weekday_int=weekday_int,
                holiday=holiday,
            )

            worked_hours = hours_by_day.get(day, empty_periods())

            balance_by_day[day] = {
                period: worked_hours.get(period, 0) - staffing_hours.get(period, 0)
                for period in PERIODS
            }
        
        # must filter before adding to table data, to get to each center's balance separately
        if filter_type:
            balance_by_day = staffing_filter(balance_by_day, filter_type)

        center_data[center.abbreviation] = balance_by_day
    
    table_data["balance"] = center_data
    return table_data


def build_sumtable(center, table_data, template, month=None):
    if template == "sum_days_base":
        shifts = TemplateShift.objects.filter(
            center=center,
            user__is_active=True,
            user__is_invisible=False
        ).all()
    elif template == "sum_days_month":
        shifts = Shift.objects.filter(
            center=center,
            month=month,
            user__is_invisible=False
            ).all()
        
    hours_by_day = {}
    for s in shifts:
        if template == "sum_days_base":
            key = f"{s.weekday}-{s.index}"
        elif template == "sum_days_month":
            key = f"{s.day}"
        
        if key not in hours_by_day:
            hours_by_day[key] = {"day": 0, "night": 0}
        s_hours = s.get_hours_count()
        hours_by_day[key]["day"] += s_hours.get("day")
        hours_by_day[key]["night"] += s_hours.get("night")
    
    # add zeroes for missing days
    if template == "sum_days_base":
        for i in range(7):
            for j in range(1, 6):
                key = f"{i}-{j}"
                if key not in hours_by_day:
                    hours_by_day[key] = {"day": 0, "night": 0}
    elif template == "sum_days_month":
        for i in range(1, month.size + 1):
            key = f"{i}"
            if key not in hours_by_day:
                hours_by_day[key] = {"day": 0, "night": 0}

    table_data["days"] = hours_by_day
    
    return table_data


def build_basetable(center, table_data, template=None, month=None):
    if template == "basetable":
        doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    elif template == "month_table":
        doctors = month.users.order_by("name").all()

    table_data["doctors"] = []
    for doctor in doctors:
        if template == "month_table":
            all_shifts = Shift.objects.filter(user=doctor, month=month, center=center).all()
        else:
            all_shifts = TS.objects.filter(user=doctor, center=center).all()

        shifts = translate_to_table(all_shifts)

        table_data["doctors"].append({"name": doctor.name,
                                      "abbr_name": doctor.abbr_name,
                                      "crm": doctor.crm,
                                      "shifts": shifts,})
    
    return table_data


def build_doctor_table(doctor, center, table_data):
    shifts = TS.objects.filter(user=doctor, center=center).all()
    shifts = translate_to_table(shifts)
    
    table_data["weekdays"] = []
    for i, day in enumerate([d[:3] for d in DIAS_SEMANA]):
        table_data["weekdays"].append({"dayID": i, "label": day})

    table_data["doctor"] = {
        "name": doctor.name,
        "abbr_name": doctor.abbr_name,
        "crm":doctor.crm,
        "shifts": shifts,
    }

    return table_data