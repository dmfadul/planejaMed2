from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Custom user manager."""

    def create_user(self, crm, name, password=None, **extra_fields):
        """Create and return a new user."""
        if not crm:
            raise ValueError('Users must have a crm number')
        if not name:
            raise ValueError('Users must have a name')
        
        normalized_name = ' '.join([n.capitalize() for n in name.split()])

        user = self.model(crm=crm, name=normalized_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, crm, password):
        """Create and return a new superuser."""
        user = self.create_user(crm=crm,
                                name="Admin",
                                password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using crm instead of email."""

    name = models.CharField(max_length=255)
    crm = models.CharField(max_length=255, unique=True)
    rqe = models.CharField(max_length=255, blank=True, default='')

    email = models.EmailField(max_length=255, default='test@example.com')
    phone = models.CharField(max_length=255, blank=True, default='')

    is_active = models.BooleanField(default=True)
    is_invisible = models.BooleanField(default=False)

    is_manager = models.BooleanField(default=False) # For vacation control
    is_staff = models.BooleanField(default=False) # For admin access. Equivalent to is_admin
    is_superuser = models.BooleanField(default=False) # Should be cced on all messages

    date_joined = models.DateTimeField(default='2020-01-01')
    compliant_since = models.DateField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'crm'    

    def __str__(self):
        return self.name
    

    @property
    def first_name(self):
        return self.name.split()[0]