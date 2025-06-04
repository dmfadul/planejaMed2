from .models import TemplateShift as TS
from .models import Center
from collections import defaultdict
from core.constants import DIAS_SEMANA, SHIFT_CODES


def gen_headers(template, month=None):
    """Generate headers for the table according to template."""

    dias_semana = [x[:3] for x in DIAS_SEMANA]
    weekdays = [""] + dias_semana * 5
    indeces = [""] + [((x - 1) // 7) + 1 for x in range(1, 36)]
    header1, header2 = [], []

    if template == "doctor_basetable":
        for i in range(6):
            if i == 0:
                header1.append({"cellID": 'corner1', "label": ""})
                continue
            header1.append({"cellID": i, "label": i})
    
    elif template in ["basetable", "sum_days_base"]:
        if template == "sum_days_base":
            weekdays = [""] + [x[0] for x in weekdays[1:]]

        for i, day in enumerate(weekdays):
            if i == 0:
                header1.append({"cellID": "corner1", "label": ""})
                header2.append({"cellID": "corner2", "label": ""})
                continue
            
            header1.append({"cellID": f"{(i-1)%7}-{indeces[i]}", "label": day, "title": DIAS_SEMANA[(i-1)%7]})
            header2.append({"cellID": f"index-{indeces[i]}", "label": indeces[i], "title": indeces[i]})

    elif template == "month_table":
        if month is None:
            raise ValueError("Month must be provided for month_table template.")
        
        for i, date in enumerate(month.gen_date_row()):
            if i == 0:
                header1.append({"cellID": "corner1", "label": ""})
                header2.append({"cellID": "corner2", "label": ""})
                continue
            
            header1.append({"cellID": f"wday-{date.day}", "label": dias_semana[date.weekday()]})
            header2.append({"cellID": f"mday-{date.day}", "label": date.day})

    elif template == "sum_doctors_base":
        centers = [None] + [
            abbr for c in Center.objects.filter(is_active=True)
            for abbr in [c.abbreviation, c.abbreviation]
        ] + ["TOTAL", "TOTAL"]

        for i, center_abbr in enumerate(centers):
            if i == 0:
                header1.append({"cellID": "corner1", "label": ""})
                header2.append({"cellID": "corner2", "label": ""})
                continue
            

            if i % 2 == 0:
                hour_type = ("Plantão", "overtime")
            else:
                hour_type = ("Rotina", "normal")

            header1.append({"cellID": f"{center_abbr}-{hour_type[1]}", "label": center_abbr})
            header2.append({"cellID": f"{hour_type[1]}-{center_abbr}", "label": hour_type[0]})

    return header1, header2
    