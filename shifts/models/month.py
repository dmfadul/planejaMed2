from django.db import models
from core.models import User
from core.constants import SHIFTS_MAP, DIAS_SEMANA


class Month(models.Model):
    year = models.IntegerField()
    number = models.IntegerField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='month_leader')
    is_current = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.year}-{self.number}"
    

    @classmethod
    def new_month(cls, number, year):
        from core.constants import LEADER

        new_month = cls(year=year, number=number)
        new_month.leader = User.objects.get(crm=LEADER.get('crm'))
        new_month.save()

        return new_month


    def gen_month_headers(self):
        header1, header2 = [], []
        for i in range(1, 36):
            header1.append({"cellID": f"{i}", "label": i})
            header2.append({"cellID": f"index-{i}", "label": i})

        return header1, header2


    @staticmethod
    def gen_headers(template):
        """Generate headers for the table according to template."""
        if template == "doctor_basetable":
            header = []
            for i in range(6):
                if i == 0:
                    header.append({"cellID": 'corner1', "label": ""})
                    continue
                header.append({"cellID": i, "label": i})
            return header, []
        
        elif template == "basetable":
            weekdays = [""] + [x[:3] for x in DIAS_SEMANA] * 5
            indeces = [""] + [((x - 1) // 7) + 1 for x in range(1, 36)]

            header1, header2 = [], []
            for i, day in enumerate(weekdays):
                if i == 0:
                    header1.append({"cellID": "corner1", "label": ""})
                    header2.append({"cellID": "corner2", "label": ""})
                    continue

                header1.append({"cellID": f"{(i-1)%7}-{indeces[i]}", "label": day})
                header2.append({"cellID": f"index-{indeces[i]}", "label": indeces[i]})

            return header1, header2

        elif template == "month_table":
            return [], []

class Holiday(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='holidays')
    day = models.IntegerField()
