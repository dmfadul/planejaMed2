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

    def test_template_shift_add_and_merge(self):
        user = User.objects.create_user(crm="12345", name="Test User", password="testpass")
        center = Center.objects.create(abbreviation="HUEM")
        shift1 = TemplateShift.add(user, center, 0, 1, 7, 13)
        shift2 = TemplateShift.add(user, center, 0, 1, 13, 19)  # Should merge with shift1

        assert TemplateShift.objects.count() == 1
        assert TemplateShift.objects.first().start_time == 7
        assert TemplateShift.objects.first().end_time == 19

    def test_template_conflict(self):
        user = User.objects.create_user(crm="12345", name="Test User", password="testpass")
        center1 = Center.objects.create(abbreviation="HUEM")
        center2 = Center.objects.create(abbreviation="HUEC")
        TemplateShift.add(user, center1, 1, 3, 7, 13)

        with pytest.raises(ValueError):
            TemplateShift.add(user, center1, 1, 3, 12, 14)  # Overlapping
        with pytest.raises(ValueError): 
            TemplateShift.add(user, center2, 1, 3, 12, 14)
        

