from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from vacations.models.vacations import Vacation
from shifts.models.month import Month


class VacationPay(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if not request.user.is_staff or not request.user.is_superuser:
            return Response(
                {"detail": "Acesso negado. Apenas administradores podem acessar este endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )

        month_num = request.query_params.get("month")
        year_num = request.query_params.get("year")

        month = Month.objects.filter(number=month_num, year=year_num).first()
        if not month:
            return Response(
                {"detail": "Mês e ano não encontrados."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        pay = month.calculate_vacation_pay()
        print("mn1", pay)    

        # try:
        #     start_date = datetime.fromisoformat(start_str).date()
        #     end_date = datetime.fromisoformat(end_str).date()
        # except ValueError:
        #     return Response(
        #         {"detail": "Formato de data inválido. Use YYYY-MM-DD."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if end_date < start_date:
        #     return Response(
        #         {"detail": "A data final não pode ser anterior à inicial."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        
        # vacations = Vacation.objects.filter(
        #     start_date__lte=end_date,
        #     end_date__gte=start_date,
        #     status=Vacation.VacationStatus.APPROVED
        # )
        
        # output = ""
        # for v in vacations:
        #     output += f"{v.user.name}:\n"
        #     shifts = v.calculate_pay()
        #     for s in shifts:
        #         output += f"{s}\n"
        #     output += "\n"

        output = ""
        return Response(output)