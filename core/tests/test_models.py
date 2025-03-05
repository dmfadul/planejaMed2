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
        name = 'John Doe'
        user = get_user_model().objects.create_user(
            crm=crm,
            password=password,
            name=name
        )

        self.assertEqual(user.crm, crm)
        self.assertTrue(user.check_password(password))

    def test_new_user_name_normalized(self):
        """Test the name for a new user is normalized."""
        sample_names = [
            ('1', 'John DOE', 'John Doe'),
            ('2', 'Jane SMITH', 'Jane Smith'),
            ('3', 'Alice  JOHNSON', 'Alice Johnson'),
            ('4', 'BoB  BROWN', 'Bob Brown'),
        ]
        
        for first_digit, name, expected_name in sample_names:
            user = get_user_model().objects.create_user(crm=first_digit + '2345',
                                                        password='Test123',
                                                        name=name)
            self.assertEqual(user.name, expected_name)

    def test_new_user_without_name_raises_error(self):
        """Test creating a new user without a name raises an error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(crm='1234',
                                                 password='Test123',
                                                 name=None)
            
    def test_create_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(crm='1234',
                                                         password='Test123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)