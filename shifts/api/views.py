from urllib import request
from rest_framework import status
from core.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class MonthImpactView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        print("Month impact requested")

        data = {
            "year": 2025,
            "month": 11,
            "has_risk": True,
            "items": [
                {
                    "user_id": 42,
                    "user_name": "Alice",
                    "current_entitlement_days": 10,
                    "will_expire_days": 4,
                    "reason": "Carryover expires at month boundary",
                    "can_keep": True,
                    "keep_key": "42-2025-11"
                },
                {
                    "user_id": 77,
                    "user_name": "Bruno",
                    "current_entitlement_days": 5,
                    "will_expire_days": 5,
                    "reason": "Exceeded carryover window",
                    "can_keep": False
                }
            ]
        }

        return Response(data, status=status.HTTP_200_OK)



