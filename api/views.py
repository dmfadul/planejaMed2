from core.models import User
from user_requests.models import userRequest
from django.http import JsonResponse
from shifts.models import Center, Month, Shift
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from core.constants import SHIFTS_MAP, SHIFT_CODES, HOUR_RANGE, MORNING_START

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.http import JsonResponse


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


class userRequestCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data
        print(data)
        # context = request.data.get("ctx")

        # current_user_crm = context.get("currentUserCrm")
        # card_crm = context.get("cardCrm")

        
        # parameters = {
        #     "request_type": request.data.get("action"),
        #     "requestee_crm": None,
        #     "requester_crm": context.get("currentUserCrm"),
        #     "center_abbr": context.get("center"),
        #     "month_number": context.get("monthNumber"),
        #     "year": context.get("year"),
        #     "selected_shift": request.data.get("selectedHour"),
        #     # find shift details by selected_shift
        # }
        

        # if current_user_crm == card_crm:
        #     pass
        # else:
        #     parameters["requestee_crm"] = card_crm


        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


@require_GET
def users_list(request):
    exclude_curr = request.GET.get('exclude_curr_user', 'false').lower() == 'true'

    users_qs = User.objects.filter(is_active=True, is_invisible=False)

    if exclude_curr and request.user.is_authenticated:
        users_qs = users_qs.exclude(id=request.user.id)

    users = [
        {
            "crm": user.crm,
            "name": user.name
        }
        for user in users_qs.order_by('name')
    ]
    return JsonResponse(users, safe=False)

@require_GET
def centers_list(request):
    centers = [{"abbr": c.abbreviation} for c in Center.objects.all()]
    return JsonResponse(centers, safe=False)


@require_GET
def month_list(request):
    months = [
        {"number": i, "name": name, "current": i == Month.objects.current().number}
        for i, name in enumerate([
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ], 1)
    ]
    return JsonResponse(months, safe=False)


@require_GET
def year_list(request):
    years = [{"year": year, "current": year == Month.objects.current().year} for year in range(2025, 2031)]
    return JsonResponse(years, safe=False)


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
        shfit_str = f"{shift.start_time:02d}:00 - {shift.end_time:02d}:00"
        schedule_dict[shift.user.crm]["shifts"].append(shfit_str)

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


@require_GET
def get_hours(request):
    crm = request.GET.get("crm")
    year = request.GET.get("year")
    month_number = request.GET.get("month")

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

    shitfs = Shift.objects.filter(**filter_kwargs).all()

    data = {}
    for s in shitfs:
        if s.user.crm not in data:
            data[s.user.crm] = {
                "name": s.user.name,
                "hours": Shift.format_hours(s.start_time, s.end_time)
            }

    response = {
        "status": "ok",
        "data": data,
        }
    return JsonResponse(response)