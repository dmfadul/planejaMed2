from django.test import TestCase
from unittest.mock import patch, call
from model_bakery import baker

from user_requests.models import UserRequest


class UserRequestNotifyTests(TestCase):
    def setUp(self):
        # setting up a UserRequest "request_pending_donation_offered"
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

        self.ur.full_clean()  # Ensure the instance is valid before saving
        self.ur.save()

    @patch("user_requests.models.notifications.Notification.from_template")
    def test_notify_request_sends_two_notifications_with_correct_payload(self, mock_from_template):
        """
        notify_request() must:
        - Send 'request_pending' to the requestee
        - Send 'request_submitted' to the requester
        - Include correct context and related_obj in both calls
        """
        self.ur.notify_request()

        # Should be called exactly twice
        self.assertEqual(mock_from_template.call_count, 2)

        # Expected shared context
        expected_context = {
            "sender_name": self.requester.name,
            "receiver_id": self.requestee.pk,
            "requestee_name": self.requestee.name,
            "center": self.shift.center.abbreviation,
            "date": "10/01/26",
            "start_hour": "07:00",
            "end_hour": "19:00",
            "target_name": self.requestee.name,
            "request_type": "DOAÇÃO",
        }

        # Build expected calls
        pending_call = call(
            template_key="request_pending_donation_offered",
            sender=self.requester,
            receiver=self.requestee,
            context=expected_context,
            related_obj=self.ur,
        )
        submitted_call = call(
            template_key="request_received",
            sender=self.requester,
            receiver=self.requester,
            context=expected_context,
            related_obj=self.ur,
        )

        # Order matters (pending first, then submitted)
        mock_from_template.assert_has_calls([pending_call, submitted_call], any_order=False)

#         # Extra safety: inspect the actual kwargs to ensure nothing critical is missing
#         first_kwargs = mock_from_template.call_args_list[0].kwargs
#         second_kwargs = mock_from_template.call_args_list[1].kwargs

#         for k in ("template_key", "sender", "receiver", "context", "related_obj"):
#             self.assertIn(k, first_kwargs)
#             self.assertIn(k, second_kwargs)

#         self.assertEqual(first_kwargs["template_key"], "request_pending")
#         self.assertEqual(first_kwargs["receiver"], self.requestee)

#         self.assertEqual(second_kwargs["template_key"], "request_submitted")
#         self.assertEqual(second_kwargs["receiver"], self.requester)

#         # Context specifics
#         self.assertEqual(first_kwargs["context"]["request_type"], "Donation")
#         self.assertEqual(first_kwargs["context"]["start_hour"], 7)
#         self.assertEqual(first_kwargs["context"]["end_hour"], 19)
#         self.assertEqual(first_kwargs["context"]["receiver_name"], self.requestee.name)
#         self.assertEqual(first_kwargs["context"]["shift_label"], str(self.shift))

#         # related_obj should be the very UserRequest instance
#         self.assertIs(first_kwargs["related_obj"], self.ur)
#         self.assertIs(second_kwargs["related_obj"], self.ur)

#     @patch("user_requests.models.notifications.Notification.from_template")
#     def test_notify_request_does_not_mutate_request_state(self, mock_from_template):
#         """
#         notify_request() should not flip is_open/is_approved/closing_date.
#         """
#         original = {
#             "is_open": self.ur.is_open,
#             "is_approved": self.ur.is_approved,
#             "closing_date": self.ur.closing_date,
#         }
#         self.ur.notify_request()
#         self.ur.refresh_from_db()
#         self.assertEqual(self.ur.is_open, original["is_open"])
#         self.assertEqual(self.ur.is_approved, original["is_approved"])
#         self.assertEqual(self.ur.closing_date, original["closing_date"])

#     def test_save_runs_clean_rules_for_donation(self):
#         """
#         save() calls full_clean(); donation without required fields should raise.
#         """
#         bad = baker.prepare(
#             "user_requests.UserRequest",
#             requester=self.requester,
#             requestee=self.requestee,
#             request_type=UserRequest.RequestType.DONATION,
#             shift=None,          # Missing
#             donor=None,          # Missing
#             donee=None,          # Missing
#         )
#         with self.assertRaisesMessage(Exception, "This field is required for a donation."):
#             bad.save()
