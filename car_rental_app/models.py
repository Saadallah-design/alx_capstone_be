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
    
# 2. Vehicle Management
class Vehicle(models.Model):
    vehicle_type_choices = [
        ('CAR', 'Car'),
        ('SCOOTER', 'Scooter'),
        ('BIG_BIKE', 'Big_Bike'),
        ('BICYCLE', 'Bicycle'),
    ]
    status_choices = [
        ('AVAILABLE', 'Available'),
        ('RENTED', 'Rented'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=20, choices=vehicle_type_choices)
    daily_rental_rate = models.DecimalField(max_digits=10, decimal_places=2)
    licence_plate = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=status_choices, default='AVAILABLE')

    def __str__(self):
        return f"{self.make} ({self.licence_plate}) - {self.agency.name}"
    
class VehicleSpecs(models.Model):
    # Choices 
    fuel_type_choices = [
        ('PETROL', 'Petrol'),
        ('DIESEL', 'Diesel'),
        ('ELECTRIC', 'Electric'),
        ('HYBRID', 'Hybrid'),
    ]
    transmission_type_choices = [
        ('MANUAL', 'Manual'),
        ('AUTOMATIC', 'Automatic'),
        ('SEMI_AUTOMATIC', 'Semi-Automatic'),
        ('NULL', 'N/A'),
    ]


    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='specs')
    transmission = models.CharField(max_length=20, choices=transmission_type_choices)
    fuel_type = models.CharField(max_length=20, choices=fuel_type_choices)
    seats = models.PositiveIntegerField()
    engine_capacity_cc = models.PositiveIntegerField(null=True, blank=True)  # Nullable for non-engine vehicles
    is_air_conditioned = models.BooleanField(default=False)
    is_helmet_included = models.BooleanField(default=False)  # Relevant for bikes and scooters

# 3. Booking & Rental Management

"""
this is considered the source of truth for all bookings made in the system
i should make sure to address the issue of overlapping bookings in the business logic layer
i can use postgres indexing for high and efficient date-range conflict checks

==> The Booking model connects the customer, 
the rental agency, the specific vehicle, 
and the time period of the rental.
"""

class Booking(models.Model):
    booking_status_choices = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    # FK to point to the rented vehicle
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')

    #  link to the user who made the booking
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')

    #  link the agency who owns the vehicle processing the booking
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='bookings')

    
    pickup_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pickup_bookings')
    dropoff_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='dropoff_bookings')

    # rental period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # total cost for the rental period | calculated at booking time | not updated dynamically | locked after booking creation
    total_rental_cost = models.DecimalField(max_digits=10, decimal_places=2)

    booking_status = models.CharField(max_length=20, choices=booking_status_choices, default='PENDING')

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for {self.vehicle.make}"