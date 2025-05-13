from core.constants import SHIFT_CODES, HOUR_RANGE, DIAS_SEMANA
from .models import TemplateShift as TS
from .utils import translate_to_table
from core.models import User
from .models import Month


def build_table_data(center, table_type, template, doctor=None, month=None, year=None):
    table_data = {
        "center": center.abbreviation,
        "month": 0,
        "year": 0,
        "table_type": table_type,
        "template": template,
        "shift_codes": ["-"] + SHIFT_CODES,
        "hour_range": [f"{x:02d}:00" for x in HOUR_RANGE],
        "hour_values": [x for x in HOUR_RANGE]
    }
    if template == "doctor_basetable":
        return build_doctor_table(doctor, center, table_data)
    
    if template == "basetable":
        return build_basetable(center, table_data)

    if template == "month_table":
        return build_month_table(center, table_data)


def build_month_table(center, table_data):
    return "unimplemented"


def build_basetable(center, table_data):
    header1, header2 = Month.gen_headers()
    table_data["header1"] = header1
    table_data["header2"] = header2

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
    
    table_data["header1"] = []
    for i in range(6):
        if i == 0:
            table_data["header1"].append({"cellID": 'corner1', "label": ""})
            continue

        table_data["header1"].append({"cellID": i, "label": i})

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