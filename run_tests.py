# user_requests/run_method.py

import sys
import os
import django

# 👇 Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planejaMed2.settings")
django.setup()

# Now safe to import your models
from user_requests.models import UserRequest, Notification
from shifts.models import Shift
from core.models import User
from vacations.models import Vacation, complianceHistory
from vacations.models.complianceHistory import ComplianceHistory

user = User.objects.filter(crm="40506").first()
print("User:", user.compliant_since)


# FINAL TASKS:
# TODO: add alert (have to keep following the vacation compliance rules) to vacation authorization message.
# TODO: add tests


# NEXT MONTH'S TASKS:
# TODO: fix bug when creating/unlocking month from users hours view.
# TODO: there are incorrect hours (ex: d: 07:00 - 13:00) in hours selection menu.
# TODO: Remove urgency hours from vacation payment calculation. (only routine hours should be considered)
# TODO: FINANCIAL MODULE

# LONG TERM TASKS:
# TODO: change letters by numbers (with ª, º) in summation tables. Or use two letters for better clarity.
# TODO: add counting to HORAS-MÉDICO table.

# POSSIBLE FUTURE TASKS:
# add an automatic email notification to users when their compliance status changes.
# add an automatic password reset email functionality.