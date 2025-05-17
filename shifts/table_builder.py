from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from .models import TemplateShift as TS
from .utils import translate_to_table, gen_headers
from core.models import User
from .models import Month


def build_table_data(center, table_type, template, doctor=None, month=None):
    header1, header2 = gen_headers(template)
    table_data = {
        "header1": header1,
        "header2": header2,
        "center": center.abbreviation,
        "month": 0,
        "year": 0,
        "table_type": table_type,
        "template": template,
        "shift_codes": ["-"] + SHIFT_CODES,
        "hour_range": [f"{x:02d}:00" for x in HOUR_RANGE],
        "hour_values": {f"{x:02d}:00": x for x in HOUR_RANGE},
    }

    if template == "doctor_basetable":
        return build_doctor_table(doctor, center, table_data)
    
    if template == "basetable":
        return build_basetable(center, table_data)

    if template == "month_table":
        table_data["header1"], table_data["header2"] = gen_headers(template, month)
        return build_month_table(month, center, table_data)


def build_month_table(month, center, table_data):
    return table_data


def build_basetable(center, table_data):
    doctors = User.objects.filter(is_active=True, is_invisible=False).order_by("name")
    table_data["doctors"] = []
    for doctor in doctors:
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