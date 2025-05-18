import pytest
from django.test import TestCase
from core.models import User
from shifts.models import Center, Month, Shift
from shifts.models import TemplateShift as TS

class TestMonthModel(TestCase):
    def test_populate_month_creates_shifts_from_template(self):
        # Setup users
        active_user = User.objects.create_user(crm="111", name="Active", password="pass")
        inactive_user = User.objects.create_user(crm="222", name="Inactive", password="pass", is_active=False)

        # Setup center and months
        center = Center.objects.create(abbreviation="HUEM")
        leader = User.objects.create_user(crm="33333", name="Leader", password="pass")
        month1 = Month.objects.create(year=2025, number=5, leader=leader)
        month2 = Month.objects.create(year=2025, number=6, leader=leader)

        # TemplateShifts: 2 for active user, 1 for inactive
        ts1 = TS.add(active_user, center, week_day=0, week_index=1, start_time=7, end_time=13)  # day 05
        ts2 = TS.add(active_user, center, week_day=2, week_index=2, start_time=13, end_time=19)  # day 14
        ts3 = TS.add(active_user, center, week_day=5, week_index=3, start_time=13, end_time=19)  # day 17
        ts4 = TS.add(active_user, center, week_day=6, week_index=4, start_time=13, end_time=19)  # day 25/05 and 27/04
        ts5 = TS.add(active_user, center, week_day=1, week_index=5, start_time=13, end_time=19)  # day 29/04
        ts6 = TS.add(inactive_user, center, week_day=1, week_index=1, start_time=7, end_time=13)  # day 06 should be ignored

        # Expected days for month1
        expected_days = {
            ts1.id: [5],       # 1st Monday of May 2025
            ts2.id: [14],      # 2nd Wednesday
            ts3.id: [17],      # 3rd Saturday
            ts4.id: [25, 27],  # 4th Sunday (May 25 and Apr 27 from previous month)
            ts5.id: [29],      # 5th Tuesday (April 29 from previous month)
            # ts6 is inactive and should not produce shifts
        }

        # Act: populate only first month
        month1.populate_month()

        # Ensure no shifts created for month2
        assert Shift.objects.filter(month=month2).count() == 0

        # # Act: populate second month
        # month2.populate_month()

        # Assert: only ts6 not used, ts4 generated 2 shifts and only for month1
        shifts1 = Shift.objects.filter(month=month1)
        assert shifts1.count() == 6


        # Validate that each expected day appears exactly once
        actual_days = sorted([shift.day for shift in shifts1])
        flat_expected_days = sorted([day for days in expected_days.values() for day in days])

        assert actual_days == flat_expected_days, f"Expected {flat_expected_days}, got {actual_days}"

        for shift in shifts1:
            assert shift.user == active_user
            assert shift.center == center
            assert shift.month == month1


