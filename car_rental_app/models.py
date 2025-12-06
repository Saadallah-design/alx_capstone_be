from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# 1. Authentication & Agency Management
# using AbsatractBaseUser for custom user model
# custom user to allow dual roles and email login
class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_agency_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    

#this one stores the business details of the rental company. 
# the oentoone link ensures only one agency profile per agency user account
class Agency(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='users')
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

# used as a choice field or FK in the Booking model to standardize pickup and dropoff locations    
class Location(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    address = models.TextField()

    is_pickup_point = models.BooleanField(default=False)
    is_dropoff_point = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.agency.name}"