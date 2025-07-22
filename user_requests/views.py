import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from shifts.models import Center, Month

logger = logging.getLogger(__name__)


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
