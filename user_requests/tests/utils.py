from user_requests.models.utils import get_context, get_template_key
from user_requests.models import UserRequest, VacationRequest

from model_bakery import baker
from django.test import TestCase


class UtilsTestCase(TestCase):
    def setUp(self):
        # setting up the necessary objects for testing
        self.requester = baker.make("core.User")
        self.requestee = baker.make("core.User")
        self.donor = baker.make("core.User")
        self.donee = baker.make("core.User")
        self.month = baker.make("shifts.Month", number=1, year=2026)
        self.shift = baker.make("shifts.Shift", month=self.month, day=10)

        self.ur = baker.make(
            UserRequest,
            requester=self.requester,
            requestee=self.requestee,
            request_type=UserRequest.RequestType.DONATION,
            audience=UserRequest.Audience.INDIVIDUAL,
            shift=self.shift,
            donor=self.requester,
            donee=self.requestee,
            start_hour=7,
            end_hour=19,
        )

        self.vr = baker.make(
            VacationRequest,
            requester=self.requester,
            request_type=VacationRequest.VacationType.REGULAR,
            start_date="2026-01-10",
            end_date="2026-01-15",
        )

    def test_vacation_request_context(self):
        for vacation_type in VacationRequest.VacationType.values:
            pass
            