"""
Test cases for Shift models.
"""
import pytest
from django.test import TestCase
from shifts.models import TemplateShift, Shift
from core.models import User
from core.constants import SHIFTS_MAP
from shifts.models.month import Month
from shifts.models import Center  # adjust import if needed


class TestTemplateShift(TestCase):
    def test_hour_list_wraps_midnight(self):
        shift = TemplateShift(start_time=22, end_time=2)
        assert shift.hour_list == [22, 23, 0, 1]

    def test_convert_to_hours(self):
        for key, value in SHIFTS_MAP.items():
            start, end = value
            assert TemplateShift.convert_to_hours(key) == (start, end)

    def test_convert_to_code_exact_match(self):
        assert TemplateShift.convert_to_code(7, 7) == "dn"
        assert TemplateShift.convert_to_code(7, 1) == "dc"
        assert TemplateShift.convert_to_code(7, 19) == "d"
        assert TemplateShift.convert_to_code(19, 7) == "n"
        assert TemplateShift.convert_to_code(7, 13) == "m"
        assert TemplateShift.convert_to_code(13, 19) == "t"
        assert TemplateShift.convert_to_code(19, 1) == "c"
        assert TemplateShift.convert_to_code(1, 7) == "v"
        assert TemplateShift.convert_to_code(13, 7) == "tn"
        assert TemplateShift.convert_to_code(13, 1) == "tc"

    def test_convert_to_code_partial(self):
        assert TemplateShift.convert_to_code(7, 12) == "d5"
       
    def test_template_shift_merging_various_cases(self):
        user = User.objects.create_user(crm="12345", name="Test User", password="testpass")
        center = Center.objects.create(abbreviation="HUEM")

        # Base shift
        shift1 = TemplateShift.add(user, center, 0, 1, 7, 13)

        # Overlapping shift
        shift2 = TemplateShift.add(user, center, 0, 1, 9, 12)
        assert TemplateShift.objects.count() == 1
        shift = TemplateShift.objects.first()
        assert shift.start_time == 7
        assert shift.end_time == 13

        # Adjacent shift
        shift3 = TemplateShift.add(user, center, 0, 1, 13, 15)
        assert TemplateShift.objects.count() == 1
        shift = TemplateShift.objects.first()
        assert shift.start_time == 7
        assert shift.end_time == 15

        # Non-overlapping shift (different weekday)
        shift4 = TemplateShift.add(user, center, 1, 1, 7, 8)
        assert TemplateShift.objects.count() == 2  # new shift added
        shifts = TemplateShift.objects.filter(weekday=1)
        assert shifts.count() == 1
        assert shifts.first().start_time == 7
        assert shifts.first().end_time == 8

        # New set of tests
        TemplateShift.objects.all().delete()
        shift1 = TemplateShift.add(user, center, 0, 1, 15, 2)

        # Midnight wraparound shift
        shift5 = TemplateShift.add(user, center, 0, 1, 8, 16)
        assert TemplateShift.objects.count() == 1
        shift = TemplateShift.objects.first()
        assert shift.start_time == 8
        assert shift.end_time == 2

        # Overlapping with midnight shift
        shift6 = TemplateShift.add(user, center, 0, 1, 23, 7)
        assert TemplateShift.objects.count() == 1
        shift = TemplateShift.objects.first()
        assert shift.start_time == 8
        assert shift.end_time == 7

        # Crossing day-break
        shift7 = TemplateShift.add(user, center, 0, 1, 7, 8)
        assert TemplateShift.objects.count() == 1
        shift = TemplateShift.objects.first()
        assert shift.start_time == 7
        assert shift.end_time == 7


    def test_other_center_conflict(self):
        user = User.objects.create_user(crm="12345", name="Test User", password="testpass")
        center1 = Center.objects.create(abbreviation="HUEM")
        center2 = Center.objects.create(abbreviation="HUEC")
        TemplateShift.add(user, center1, 1, 3, 7, 13)

        with pytest.raises(ValueError): 
            TemplateShift.add(user, center2, 1, 3, 12, 14)
    
    
    def test_other_center_no_conflict(self):
        user = User.objects.create_user(crm="12345", name="Test User", password="testpass")
        center1 = Center.objects.create(abbreviation="HUMM")
        center2 = Center.objects.create(abbreviation="HUCC")
        
        base_shift = TemplateShift.add(user, center1, 1, 3, 7, 13)

        assert TemplateShift.objects.count() == 1

        other_shift = TemplateShift.add(user, center2, 1, 3, 13, 19)
        
        assert TemplateShift.objects.count() == 2