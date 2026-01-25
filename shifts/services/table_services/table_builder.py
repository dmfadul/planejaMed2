from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from .table_utils import translate_to_table, gen_headers
from shifts.models import Center, Month, Shift, TemplateShift
from shifts.models import TemplateShift as TS
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


def build_doctors_sumtable(table_data, template, month=None):
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
            print("hours_dict", hours_dict)
            
            shifts[cell_id_over] += hours_dict["overtime"]
            shifts[cell_id_norm] += hours_dict["normal"]      
            
            total_overtime += hours_dict["overtime"]
            total_normal += hours_dict["normal"]
        
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
        
        shifts[cell_id_tot_over] = total_overtime
        shifts[cell_id_tot_norm] = total_normal

        table_data["doctors"].append({"name": doctor.name,
                                      "abbr_name": doctor.abbr_name,
                                      "crm": doctor.crm,
                                      "shifts": shifts,})
    
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