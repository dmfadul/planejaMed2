from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from .utils import translate_to_table, gen_headers
from .models import Month, Shift, TemplateShift
from .models import TemplateShift as TS
from collections import defaultdict
from core.models import User


def build_table_data(table_type, template, center=None, doctor=None, month=None):
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
    }
    if center:
        table_data["center"] = center.abbreviation
    

    if template == "basetable":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        return build_basetable(center, table_data)

    if template == "month_table":
        table_data["header1"], table_data["header2"] = gen_headers(template, month)
        table_data["month"] = month.number
        table_data["year"] = month.year
        return build_basetable(center, table_data, template=template)
    
    if template == "doctor_basetable":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["show_back_button"] = 1
        return build_doctor_table(doctor, center, table_data)
    
    if template == "sum_days_base":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["show_back_button"] = 1
        return build_sumtable(center, table_data, template=template)
    
    if template == "sum_days_month":
        return []
    
    if template == "sum_doctors_base":
        table_data["header1"], table_data["header2"] = gen_headers(template)
        table_data["center"] = ""
        return build_doctors_sumtable(table_data, template)
    
    if template == "sum_doctors_month":
        return []


def build_doctors_sumtable(table_data, template):
    return table_data


def build_sumtable(center, table_data, template, month=None):
    if template == "sum_days_base":
        base_shifts = TemplateShift.objects.filter(center=center)
        
        hours_by_day = {}
        for bs in base_shifts:
            if f"{bs.weekday}-{bs.index}" not in hours_by_day:
                hours_by_day[f"{bs.weekday}-{bs.index}"] = {"day": 0, "night": 0}
            bs_hours = bs.get_hours_count()

            hours_by_day[f"{bs.weekday}-{bs.index}"]["day"] += bs_hours.get("day")
            hours_by_day[f"{bs.weekday}-{bs.index}"]["night"] += bs_hours.get("night")

        # add zeroes for missing days
        for i in range(7):
            for j in range(1, 6):
                key = f"{i}-{j}"
                if key not in hours_by_day:
                    hours_by_day[key] = {"day": 0, "night": 0}

        table_data["days"] = hours_by_day
    
    return table_data


def build_basetable(center, table_data, template=None):
    doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    table_data["doctors"] = []
    for doctor in doctors:
        if template == "month_table":
            shifts = Shift.objects.filter(user=doctor, center=center).all()
        else:
            shifts = TS.objects.filter(user=doctor, center=center).all()

        shifts = translate_to_table(shifts)
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