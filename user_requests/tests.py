from django.test import TestCase
from unittest.mock import patch, call
from user_requests.models import UserRequest


try:
    from model_bakery import baker
    HAS_BAKERY = True
except Exception:
    HAS_BAKERY = False


