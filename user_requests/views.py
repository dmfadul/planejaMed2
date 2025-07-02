import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from shifts.models import Month

logger = logging.getLogger(__name__)


@login_required
def calendar(request, center_abbr):
    month = Month.objects.current()
    if not month:
        logger.error("No current month found.")
        return render(request, "user_requests/error.html", {"message": "No current month available."})

    print(f"Current month: {month.name} ({month.year})")
    return render(request, "user_requests/calendar.html")
