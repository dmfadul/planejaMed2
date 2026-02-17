from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from vacations.models.vacations import Vacation


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

        
        print("m", month_num, type(month_num), year_num, type(year_num))    
        # start_str = request.query_params.get("start")
        # end_str = request.query_params.get("end")

        # if not start_str or not end_str:
        #     return Response(
        #         {"detail": "Parâmetros 'start' e 'end' são obrigatórios."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

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