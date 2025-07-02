import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@login_required
def calendar(request):
    return render(request, "user_requests/calendar.html")
