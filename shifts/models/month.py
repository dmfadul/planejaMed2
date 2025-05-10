from django.db import models
from core.models import User
from core.constants import SHIFTS_MAP, DIAS_SEMANA



class Month(models.Model):
    year = models.IntegerField()
    number = models.IntegerField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='month_leader')
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)


    @staticmethod
    def gen_headers():
        """Generate headers for the table."""
        weekdays = [""] + [x[:3] for x in DIAS_SEMANA] * 5
        indeces = [""] + [((x - 1) // 7) + 1 for x in range(1, 36)]

        header1 = []
        header2 = []
        for i, day in enumerate(weekdays):
            if i == 0:
                header1.append({"cellID": "corner1", "label": ""})
                header2.append({"cellID": "corner2", "label": ""})
                continue

            header1.append({"cellID": f"{(i-1)%7}-{indeces[i]}", "label": day})
            header2.append({"cellID": f"index-{indeces[i]}", "label": indeces[i]})

        return header1, header2


class Holiday(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
    day = models.IntegerField()
