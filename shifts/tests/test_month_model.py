import pytest
from django.test import TestCase
from core.models import User
from shifts.models import Center, Month, TemplateShift, Shift

class TestMonthModel(TestCase):
    def test_populate_month_creates_shifts_from_template(self):
        # Setup users
        active_user = User.objects.create_user(crm="111", name="Active", password="pass")
        inactive_user = User.objects.create_user(crm="222", name="Inactive", password="pass", is_active=False)

        # Setup center and months
        center = Center.objects.create(abbreviation="HUEM")
        month1 = Month.objects.create(year=2025, month=5)
        month2 = Month.objects.create(year=2025, month=6)

        # TemplateShifts: 2 for active user, 1 for inactive
        ts1 = TemplateShift.add(active_user, center, week_day=0, week_index=0, start_time=7, end_time=13)  # day 0
        ts2 = TemplateShift.add(active_user, center, week_day=2, week_index=1, start_time=13, end_time=19)  # day 9
        ts3 = TemplateShift.add(inactive_user, center, week_day=1, week_index=0, start_time=7, end_time=13)  # should be ignored

        # Act: populate only first month
        month1.populate_month()

        # Assert: only ts1 and ts2 used, and only for month1
        shifts = Shift.objects.filter(month=month1)
        assert shifts.count() == 2

        days = [s.day for s in shifts]
        assert set(days) == {0, 9}
        for shift in shifts:
            assert shift.user == active_user
            assert shift.center == center
            assert shift.month == month1

        # Ensure no shifts created for month2
        assert Shift.objects.filter(month=month2).count() == 0
