from django.db import models

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
    # Updated reference to 'core.Agency'
    owner_agency = models.ForeignKey('core.Agency', on_delete=models.CASCADE, related_name='vehicles', blank=True, null=True)
    make = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=20, choices=vehicle_type_choices)
    daily_rental_rate = models.DecimalField(max_digits=10, decimal_places=2)
    licence_plate = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=status_choices, default='AVAILABLE')

    def __str__(self):
        return f"{self.make} ({self.licence_plate}) - {self.owner_agency.agency_name}"
    
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
        ('NA', 'N/A'),
    ]


    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='specs')
    transmission = models.CharField(max_length=20, choices=transmission_type_choices)
    fuel_type = models.CharField(max_length=20, choices=fuel_type_choices)
    seats = models.PositiveIntegerField()
    engine_capacity_cc = models.PositiveIntegerField(null=True, blank=True)  # Nullable for non-engine vehicles
    is_air_conditioned = models.BooleanField(default=False)
    is_helmet_included = models.BooleanField(default=False)  # Relevant for bikes and scooters
