from urllib import request
from rest_framework import status
from core.permissions import IsAdmin
from shifts.models import Center, Month
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CenterSerializer,
    MonthSerializer
)


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


class MonthAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, selector=None, *args, **kwargs):
        if selector == "current":
            # Return current month info
            current_month = Month.objects.current()
            serializer = MonthSerializer(current_month)
            print("Fetching current month info  for user:", serializer.data)
        else:
            try:
                month_id = int(selector)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "Invalid month. Use 'current' or a number from 1 to 12."},
                    status=status.HTTP_400_BAD_REQUEST,
                )        
            
            month = get_object_or_404(Month, number=month_id)
            serializer = MonthSerializer(month)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CenterAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """Retrieve center(s)."""
        if pk is not None:
            # Fetch and return the specific center details
            center = get_object_or_404(Center, pk=pk)
            serializer = CenterSerializer(center)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Fetch and return the list of centers
        centers = Center.objects.all()
        serializer = CenterSerializer(centers, many=True)
        print("Centers retrieved:", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        """Create a new center."""
        serializer = CenterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def put(self, request, pk=None):
        """Update an existing center."""
        center = get_object_or_404(Center, pk=pk)
        serializer = CenterSerializer(center, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk=None):
        """Delete a center."""
        center = get_object_or_404(Center, pk=pk)
        center.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)