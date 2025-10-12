from core.models import User
from django.db import transaction
from django.http import JsonResponse
from user_requests.models import UserRequest
from shifts.models import Center, Month, Shift
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from core.constants import SHIFTS_MAP, SHIFT_CODES, HOUR_RANGE, MORNING_START
from .serializers import ShiftSerializer, UserRequestSerializer, NotificationSerializer

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
        action = data.get('action')

        # --- Check for required fields ---
        requestee_needed = action in ("ask_for_donation",
                                      "offer_donation",
                                      "exchange") # change when implementing exchange
        requestee_crm = data.get('cardCRM')
        if requestee_needed and not requestee_crm:
            return Response(
                {"error": "Campos obrigatórios (cardCRM) ausentes."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # --- Parse and validate hours ---
        shift_raw = data.get('shift')
        if action in ["include"] and shift_raw == "-":
            start_hour_raw, end_hour_raw = data.get('startHour'), data.get('endHour')
            shift_id = None
        elif action in ["include"]:
            start_hour_raw, end_hour_raw = Shift.convert_to_hours(shift_raw)
            shift_id = None
        elif action not in ["include"]:
            start_hour_raw, end_hour_raw = data.get('startHour'), data.get('endHour')
            shift_id = shift_raw
        
        try:
            start_hour = int(start_hour_raw)
            end_hour = int(end_hour_raw)
        except (TypeError, ValueError):
            return Response(
                {"error": "Horas inválidas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not shift_id and action not in ["include"]:
            return Response(
                {"error": "Campos obrigatórios (shift) ausentes."},
                status=status.HTTP_400_BAD_REQUEST
            )
        shift = get_object_or_404(Shift, pk=int(shift_id)) if shift_id is not None else None


        requester = request.user
        if requestee_needed:
            requestee = get_object_or_404(User, crm=requestee_crm)
        else:
            requestee = None
        
        if requester == requestee:
            return Response(
                {"error": "Você não pode doar para si mesmo."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # --- Decide Donor and Donee ---
        if action == "ask_for_donation":
            donor, donee = requestee, requester
            check_for_conflicts = True
            request_type = UserRequest.RequestType.DONATION
        elif action == "offer_donation":
            donor, donee = requester, requestee
            check_for_conflicts = True
            request_type = UserRequest.RequestType.DONATION
        elif action == "exclusion":
            donor, donee = get_object_or_404(User, crm=data.get('cardCRM')), None
            check_for_conflicts = False
            request_type = UserRequest.RequestType.EXCLUDE
        elif action == "include":
            donor, donee = None, get_object_or_404(User, crm=data.get('cardCRM'))
            check_for_conflicts = True
            request_type = UserRequest.RequestType.INCLUDE
        else:
            return Response(
                {"error": "Ação inválida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if check_for_conflicts:
            conflict = Shift.check_conflict(
                donee,
                month=shift.month if shift else Month.get_current(),
                day=shift.day,
                start_time=start_hour,
                end_time=end_hour
            )
            if conflict:
                return Response(
                    {
                        "Conflito de Horário":
                            f"O usuário {getattr(donee, 'name', donee)} já está inscrito no centro "
                            f"{conflict.center.abbreviation} no dia {conflict.day}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        params = {
            "requester":    requester.id,
            "request_type": request_type,
            "requestee":    requestee.id if requestee else None,
            "donor":        donor.id if donor else None,
            "donee":        donee.id if donee else None,
            "shift":        shift.id if shift else None,
            "start_hour":   start_hour,
            "end_hour":     end_hour,
        }

        serializer = UserRequestSerializer(data=params)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            instance = serializer.save()
            # Try to notify but don't fail the whole transaction if it fails
            # try:
            instance.notify_request()
            # except Exception as e:
            #     # add logging here
            #     return Response(
            #         {"status": "created", "id": instance.id, "warning": "Notificação falhou."},
            #         status=status.HTTP_201_CREATED
            #     )
        return Response(
            {"status": "created", "id": instance.id, "request_type": instance.request_type},
            status=status.HTTP_201_CREATED
        )

@api_view(["GET"])
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

    shifts = Shift.objects.filter(**filter_kwargs).all()
    serializer = ShiftSerializer(shifts, many=True)

    return Response(serializer.data)
    

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
