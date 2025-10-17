import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from shifts.models import Center, Month, Shift

logger = logging.getLogger(__name__)


@login_required
def schedule(request):
    user = request.user
    month = Month.objects.current()
    if not month:
        logger.error("No current month found.")
        return render(request, "user_requests/error.html", {"message": "No current month available."})

    shifts = Shift.objects.filter(user=user, month=month).order_by('center__abbreviation', 'day', 'start_time')

    schedule_data = []
    for s in shifts:
        shift_date = s.date.strftime("%d/%m/%Y")
        str_hr = f"{s.start_time:02d}:00"
        end_hr = f"{s.end_time:02d}:00"
        sch_line = f"{s.center.abbreviation} -- {shift_date} -- {str_hr} - {end_hr}"

        schedule_data.append({"shift_id": s.id, "line": sch_line})

    return render(request, "user_requests/schedule.html", context={"schedule_data": schedule_data})

@login_required
def calendar(request, center_abbr):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = Month.objects.current()
    if not month:
        logger.error("No current month found.")
        return render(request, "user_requests/error.html", {"message": "No current month available."})

    calendar_data  = {
        "current_user_crm": request.user.crm,
        "open_center": center,
        "month_number": month.number,
        "month_name": month.name,
        "year": month.year,
        "table": month.gen_calendar_table(),
    }
    
    return render(request, "user_requests/calendar.html", context=calendar_data)


@login_required
def notifications(request):
    return render(request, "user_requests/notifications.html", context={})