"""
Test cases for Shift models.
"""
import pytest
from shifts.models import Shift, TemplateShift
from core.models import User
from shifts.models.month import Month
from shifts.models.center import Center

@pytest.fixture
def user(db):
    return User.objects.create(username="drtest")

@pytest.fixture
def center(db):
    return Center.objects.create(name="Center A", abbreviation="CA")

@pytest.fixture
def month(db):
    return Month.objects.create(name="May", year=2025)
