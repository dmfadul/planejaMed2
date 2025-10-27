from core.models import User
from django.db import transaction
from django.http import JsonResponse
from user_requests.models import UserRequest
from shifts.models import Center, Month, Shift
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from core.constants import SHIFTS_MAP, SHIFT_CODES, HOUR_RANGE, MORNING_START

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.http import JsonResponse


# TODO: move all api views to */api/ folders
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        "Submit User Request": "/api/submit_user_request/",
        "Users": "/api/users/",
        "Centers": "/api/centers/",
        "Months": "/api/months/",
        "Years": "/api/years/",
        "Hours": "/api/hours/"
    }
    
    return Response(api_urls)


# class userRequestCreate(APIView):
#     permission_classes = [permissions.IsAuthenticated]
    
#     def post(self, request):
#         ser = IncomingUserRequestSerializer(
#             data=request.data,
#             context={"request": request}
#         )

#         ser.is_valid(raise_exception=True)

#         # normalized, typed, DB-ready params:
#         params = ser.validated_data
#         req_obj = create_user_request(**params)

#         out = OutUserRequestSerializer(req_obj)
#         return Response(out.data, status=status.HTTP_201_CREATED)



# @api_view(["GET"])
# def get_hours(request):
#     month = Month.objects.current()

#     crm = request.GET.get("crm") if request.GET.get("crm") else request.user.crm
#     year = month.year
#     month_number = month.number

#     filter_kwargs = {
#         "user__crm": crm,
#         "month__year": year,
#         "month__number": month_number
#     }

#     center_abbr = request.GET.get("center")
#     if center_abbr:
#         filter_kwargs["center__abbreviation"] = center_abbr
    
#     day = request.GET.get("day", 0)
#     if day and day.isdigit():
#         filter_kwargs["day"] = int(day)

#     shifts = Shift.objects.filter(**filter_kwargs).all()
#     serializer = ShiftSerializer(shifts, many=True)

#     return Response(serializer.data)
    

@require_GET
def users_list(request):
    exclude_curr = request.GET.get('exclude_curr_user', 'false').lower() == 'true'

    users_qs = User.objects.filter(is_active=True, is_invisible=False)

    if exclude_curr and request.user.is_authenticated:
        users_qs = users_qs.exclude(id=request.user.id)

    users = [
        {
            "id": user.id,
            "crm": user.crm,
            "name": user.name
        }
        for user in users_qs.order_by('name')
    ]
    return JsonResponse(users, safe=False)


# @require_GET
# def centers_list(request):
#     centers = [{"abbr": c.abbreviation} for c in Center.objects.all()]
#     return JsonResponse(centers, safe=False)


# @require_GET
# def month_list(request):
#     months = [
#         {"number": i, "name": name, "current": i == Month.objects.current().number}
#         for i, name in enumerate([
#             "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
#             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
#         ], 1)
#     ]
#     return JsonResponse(months, safe=False)


# @require_GET
# def year_list(request):
#     years = [{"year": year, "current": year == Month.objects.current().year} for year in range(2025, 2031)]
#     return JsonResponse(years, safe=False)


# @require_GET
# def day_schedule(request, center_abbr, year, month_number, day):
#     center = get_object_or_404(Center, abbreviation=center_abbr)
#     month = get_object_or_404(Month, number=month_number, year=year)

#     day_shifts = Shift.objects.filter(
#         center=center,
#         month=month,
#         day=day
#     )
    
#     schedule_dict = {}
#     for shift in day_shifts:
#         if shift.user.crm not in schedule_dict:
#             schedule_dict[shift.user.crm] = {
#                 "user": shift.user,
#                 "shifts": []
#             }
#         schedule_dict[shift.user.crm]["shifts"].append((shift.start_time, shift.end_time))

#     for _, data in schedule_dict.items():
#         # custom order: 07..23, 00..06  -> use modular key (h - 7) % 24
#         sorted_shifts = sorted(
#             data["shifts"],
#             key=lambda t: ((t[0] - 7) % 24, t[1])  # tie-breaker by end time
#         )
#         # format "HH:00 - HH:00"
#         data["shifts"] = [f"{s:02d}:00 - {e:02d}:00" for s, e in sorted_shifts]
        
#     # Convert the schedule dictionary to a list of dictionaries
#     schedule_data = []
#     for values in schedule_dict.values():
#         user_name = values["user"].name
#         shifts_str = "<br>".join(values["shifts"])
#         card_line = user_name + "<br>" + shifts_str
#         schedule_data.append({
#             "name": user_name,
#             "crm": values["user"].crm,
#             "cardLine": card_line,
#         })

#     schedule_data = sorted(schedule_data, key=lambda x: x["name"].lower())
        
#     return JsonResponse({
#         "status": "ok",
#         "schedule": schedule_data,
#     })
