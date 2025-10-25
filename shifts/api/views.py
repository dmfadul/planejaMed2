from rest_framework import status
from core.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response


class MonthImpactView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # TODO: implement month impact logic
        print("Month impact requested")
        return Response({"detail": "Month impact data"}, status=status.HTTP_200_OK)

    