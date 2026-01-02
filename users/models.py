from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 1. Authentication & Agency Management
# using AbsatractBaseUser for custom user model
# custom user to allow dual roles and email login
# 1. Custom Manager (Required for AbstractBaseUser)
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Your custom field for superuser creation
        extra_fields.setdefault('role', 'PLATFORM_ADMIN') 
        
        return self.create_user(username, email, password, **extra_fields)
    

# Using AbstractBaseUser with PermissionsMixin for multi-role support (agency admin, customer, staff) is appropriate for this use case.

class User(AbstractBaseUser, PermissionsMixin):
    # using ROLE choices to define user roles especially for agency admins and customers
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('AGENCY_ADMIN', 'Agency Admin'),
        ('AGENCY_STAFF', 'Agency Staff'),
        ('PLATFORM_ADMIN', 'Platform Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER', help_text='Role of the user in the system')

    USERNAME_FIELD = 'username' # <-- THIS WAS MISSING
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # using only is_staff and is_active for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin interface access
    # Without is_staff, users cannot access Django Admin, even superusers. Impact: Administration will be broken.


    objects = CustomUserManager()
    # Problem: Without this, Django won't use the custom manager. Impact: User.objects.create_user() will fail.

    # adding convenience methods for role checks
    def is_customer(self):
        return self.role == 'CUSTOMER'
    
    def is_agency_user(self):
        return self.role in ['AGENCY_ADMIN', 'AGENCY_STAFF']

    def is_agency_admin(self):
        return self.role == 'AGENCY_ADMIN'

    def is_agency_staff(self):
        return self.role == 'AGENCY_STAFF'

    def is_platform_admin(self):
        return self.role == 'PLATFORM_ADMIN'

    @property
    def agency(self):
        """
        Helper to get the agency associated with this user, 
        regardless of whether they are an owner or staff.
        """
        if self.is_agency_admin():
            return getattr(self, 'agency_profile', None)
        elif self.is_agency_staff():
            membership = getattr(self, 'agency_membership', None)
            return membership.agency if membership else None
        return None
    
    def __str__(self):
        return self.username
