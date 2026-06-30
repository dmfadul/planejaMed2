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
# TODO: add tests
# TODO: check if admin/root distictions are working properly
# TODO: add a teamLeader group and give them the ability to authorize inclusions

# VACATIONS:
# TODO: Fix (?) vacations
# TODO: Remove urgency hours from vacation payment calculation. (only routine hours should be considered)
# TODO: add alert (have to keep following the vacation compliance rules) to vacation authorization message.

# VACATION COMPLIANCE:
# TODO: do not enforce vacation rules on the month when user is on vacation
# TODO: add a compliance check:
# month creation -- check for base rights
# unlock month -- check for month rights
# TODO: check donation text ("de" and "para" seems to be confusing users)

# SHIFTS:
# TODO: fix names links (the redirects are not working properly in all kinds of tables)
# TODO: fix bug when creating/unlocking month from users hours view.
# TODO: there are incorrect hours (ex: d: 07:00 - 13:00) in hours selection menu.
# TODO: fix bug when edit button is clicked when opening a table
# TODO: remove the edit button from sumDoctor table
# TODO: add visible month/year to both the new month and unlock month modal dialogs.
# TODO: check if there is a difference between original and realized months
# TODO: finish report

# USER REQUESTS:
# TODO: user requests for a future month should be allowed
# TODO: Open requests (requests that are not for an specific user, but can be accepted by anyone)

# FINANCE:
# TODO: individual view of finance data (for each user)
# TODO: finance reports

# POSSIBLE FUTURE TASKS:
# normalize modal themes (make them all the same)
# reorganize the admin functions (make them more intuitive)
# add an automatic email notification to users when their compliance status changes.
# add an automatic password reset email functionality.