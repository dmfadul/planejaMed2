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

# Example logic:
shift1 = Shift.objects.first()
shift2 = Shift.objects.last()
user1 = User.objects.filter(crm=42173).first()
print(shift1)
print(shift2)
print(user1)

c = shift1.change_user(user1)
print(c)
# req = UserRequest.objects.first()
# req.remove_notifications()
