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
# TODO: add a vacations dashboard to the admin panel. (necessary for testing)
# TODO: transfer old vacation data from planejaMed1 to planejaMed2.
# TODO: add a vacation payment calculation function to the admin panel.

# TODO: translate from english to portuguese.
# TODO: add tests
# TODO: fix bug when creating/unlocking month from users hours view.


# NEXT MONTH'S TASKS:
# TODO: fix order in schedule (dates are not in order by month)
# TODO: userRequest has no toast notification when created.
# TODO: there are incorrect hours (ex: d: 07:00 - 13:00) in hours selection menu.
# TODO: add vacation consult/cancel options to user panel.
# TODO: FINANCIAL MODULE
# TODO: Put all user's centers together

# LONG TERM TASKS:
# TODO: Add new function to change user's alias. (Currently only admins can do that through the admin panel)
# TODO: clean up user creation form and move it to admin control (currently, only root users can create new users)
# TODO: Add new function to remove users. (currently only admins can do that through the admin panel)
# TODO: change letters by numbers (with ª, º) in summation tables. Or use two letters for better clarity.
# TODO: add counting to HORAS-MÉDICO table.

# POSSIBLE FUTURE TASKS:
# add an automatic email notification to users when their compliance status changes.
# add an automatic password reset email functionality.