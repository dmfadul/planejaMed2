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
        if not request.user.is_staff and not request.user.is_superuser:
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

        return Response(pay)