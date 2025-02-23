"""
Test cases for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test cases for models."""

    def test_create_user_with_crm_successful(self):
        """Test creating a new user with a crm is successful."""
        crm = '1234567'
        password = 'TestPass123'
        user = get_user_model().objects.create_user(
            crm=crm,
            password=password
        )

        self.assertEqual(user.crm, crm)
        self.assertTrue(user.check_password(password))

        