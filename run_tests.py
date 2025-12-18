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
# TODO: check bases sums
# TODO: transfer old vacation data from planejaMed1 to planejaMed2.


# NEXT MONTH'S TASKS:
# TODO: Put all user's centers together
# TODO: Add new function to remove users. (currently only admins can do that through the admin panel)
# TODO: Add new function to change user's alias. (Currently only admins can do that through the admin panel)
# TODO: clean up user creation form and move it to admin control (currently, only root users can create new users)


# POSSIBLE FUTURE TASKS:
# add an automatic email notification to users when their compliance status changes.
# add an automatic password reset email functionality.