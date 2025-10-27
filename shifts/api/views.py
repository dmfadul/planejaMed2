from urllib import request
from rest_framework import status
from core.permissions import IsAdmin
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from rest_framework.permissions import IsAuthenticated

from shifts.models import (
    Center,
    Month,
    Shift
)

from .serializers import (
    CenterSerializer,
    MonthSerializer,
    ShiftSerializer
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
    


@require_GET
def day_schedule(request, center_abbr, year, month_number, day):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_number, year=year)

    day_shifts = Shift.objects.filter(
        center=center,
        month=month,
        day=day
    )
    
    schedule_dict = {}
    for shift in day_shifts:
        if shift.user.crm not in schedule_dict:
            schedule_dict[shift.user.crm] = {
                "user": shift.user,
                "shifts": []
            }
        schedule_dict[shift.user.crm]["shifts"].append((shift.start_time, shift.end_time))

    for _, data in schedule_dict.items():
        # custom order: 07..23, 00..06  -> use modular key (h - 7) % 24
        sorted_shifts = sorted(
            data["shifts"],
            key=lambda t: ((t[0] - 7) % 24, t[1])  # tie-breaker by end time
        )
        # format "HH:00 - HH:00"
        data["shifts"] = [f"{s:02d}:00 - {e:02d}:00" for s, e in sorted_shifts]
        
    # Convert the schedule dictionary to a list of dictionaries
    schedule_data = []
    for values in schedule_dict.values():
        user_name = values["user"].name
        shifts_str = "<br>".join(values["shifts"])
        card_line = user_name + "<br>" + shifts_str
        schedule_data.append({
            "name": user_name,
            "crm": values["user"].crm,
            "cardLine": card_line,
        })

    schedule_data = sorted(schedule_data, key=lambda x: x["name"].lower())
        
    return JsonResponse({
        "status": "ok",
        "schedule": schedule_data,
    })


@api_view(["GET"])
def get_hours(request):
    month = Month.objects.current()

    crm = request.GET.get("crm") if request.GET.get("crm") else request.user.crm
    year = month.year
    month_number = month.number

    filter_kwargs = {
        "user__crm": crm,
        "month__year": year,
        "month__number": month_number
    }

    center_abbr = request.GET.get("center")
    if center_abbr:
        filter_kwargs["center__abbreviation"] = center_abbr
    
    day = request.GET.get("day", 0)
    if day and day.isdigit():
        filter_kwargs["day"] = int(day)

    shifts = Shift.objects.filter(**filter_kwargs).all()
    serializer = ShiftSerializer(shifts, many=True)

    return Response(serializer.data)