# from django.test import TestCase
# from unittest.mock import patch, call

# from user_requests.models import UserRequest

# # Prefer model_bakery for robust factory-free model creation
# try:
#     from model_bakery import baker
#     HAS_BAKERY = True
# except Exception:
#     HAS_BAKERY = False

# class UserRequestNotifyTests(TestCase):
#     def setUp(self):
#         if not HAS_BAKERY:
#             self.skipTest("model_bakery is required for these tests (install with `pip install model-bakery`).")

#         # Users
#         self.requester = baker.make("core.User", name="Requester R")
#         self.requestee = baker.make("core.User", name="Requestee E")
#         self.donor = baker.make("core.User", name="Donor D")
#         self.donee = baker.make("core.User", name="Donee N")

#         # Shift (baker will fill required fields; customize if your Shift enforces specifics)
#         self.shift = baker.make("shifts.Shift")

#         # Build a valid DONATION request (clean() requires donor, donee, shift)
#         self.ur: UserRequest = baker.prepare(
#             "user_requests.UserRequest",
#             requester=self.requester,
#             requestee=self.requestee,
#             request_type=UserRequest.RequestType.DONATION,
#             shift=self.shift,
#             start_hour=7,
#             end_hour=19,
#             donor=self.donor,
#             donee=self.donee,
#             is_open=True,
#             is_approved=False,
#         )
#         # save() will call full_clean(), which enforces `clean()` rules
#         self.ur.save()

#     @patch("user_requests.models.notifications.Notification.from_template")
#     def test_notify_users_sends_two_notifications_with_correct_payload(self, mock_from_template):
#         """
#         notify_users() must:
#         - Send 'request_pending' to the requestee
#         - Send 'request_submitted' to the requester
#         - Include correct context and related_obj in both calls
#         """
#         self.ur.notify_users()

#         # Should be called exactly twice
#         self.assertEqual(mock_from_template.call_count, 2)

#         # Expected shared context
#         expected_ctx = {
#             "request_type": self.ur.get_request_type_display(),  # 'Donation'
#             "receiver_name": self.requestee.name,                # Requestee's name for both messages (per model code)
#             "shift_label": str(self.shift),
#             "start_hour": self.ur.start_hour,
#             "end_hour": self.ur.end_hour,
#         }

#         # Build expected calls
#         pending_call = call(
#             template_key="request_pending",
#             sender=self.requester,
#             receiver=self.requestee,
#             context=expected_ctx,
#             related_obj=self.ur,
#         )
#         submitted_call = call(
#             template_key="request_submitted",
#             sender=self.requester,
#             receiver=self.requester,
#             context=expected_ctx,
#             related_obj=self.ur,
#         )

#         # Order matters (pending first, then submitted)
#         mock_from_template.assert_has_calls([pending_call, submitted_call], any_order=False)

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
#     def test_notify_users_does_not_mutate_request_state(self, mock_from_template):
#         """
#         notify_users() should not flip is_open/is_approved/closing_date.
#         """
#         original = {
#             "is_open": self.ur.is_open,
#             "is_approved": self.ur.is_approved,
#             "closing_date": self.ur.closing_date,
#         }
#         self.ur.notify_users()
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
