from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField

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
    # Updated reference to 'vehicles.Vehicle'
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='bookings')

    #  link to the user who made the booking
    # Updated reference to 'users.User'
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')

    #  link the agency who owns the vehicle processing the booking
    # Updated reference to 'core.Agency'
    agency = models.ForeignKey('core.Agency', on_delete=models.CASCADE, related_name='bookings')

    
    # Updated reference to 'branches.Location'
    pickup_location = models.ForeignKey('branches.Location', on_delete=models.CASCADE, related_name='pickup_bookings')
    dropoff_location = models.ForeignKey('branches.Location', on_delete=models.CASCADE, related_name='dropoff_bookings')

    # rental period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # total cost for the rental period | calculated at booking time | not updated dynamically | locked after booking creation
    total_rental_cost = models.DecimalField(max_digits=10, decimal_places=2)

    booking_status = models.CharField(max_length=20, choices=booking_status_choices, default='PENDING')


    # adding a clean method to check that end_date is after start_date
    def clean(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError("End date must be after start date.")
            
        # prevent bookings too far in the future
        max_advance_booking = 365  # 1 year in advance
        if self.start_date > timezone.now() + timedelta(days=max_advance_booking):
            raise ValidationError(f"Bookings cannot be made more than {max_advance_booking} days in advance.")

        # and here checking for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            vehicle=self.vehicle,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("This vehicle is already booked for the selected dates.")

        # Validate that the booking agency matches the vehicle's owner agency
        # since we have three connected connected pieces of data: booking, vehicle, agency
        # we need to make sure that the agency is the owner of the vehicle in order to avoid
        # the 'frankenstein' booking where the agency is not the owner of the vehicle
        # in a nutshel: It enforces the rule: "You can only book a vehicle through the agency that actually owns it.
        if self.agency != self.vehicle.owner_agency:
            raise ValidationError("The booking agency must match the vehicle's owner agency.")

    # using a save field for cost is locked at booking time. 
    # if vehicle rates change later, existing bookings remain unaffected.
    def save(self, *args, **kwargs):
        if not self.total_rental_cost:
            rental_duration = self.end_date - self.start_date
            rental_days = rental_duration.days
            
            # Grace period logic: 60 minutes (3600 seconds)
            remaining_seconds = rental_duration.seconds
            
            if rental_days == 0:
                rental_days = 1  # Minimum one day charge
            elif remaining_seconds > 3600:
                rental_days += 1  # Charge extra day if over 60 min grace period

            self.total_rental_cost = rental_days * self.vehicle.daily_rental_rate

        # call clean method to validate before saving
        self.clean()
        super().save(*args, **kwargs)

    # adding a database constraint to enforce no overlapping bookings at the DB level
    class Meta:
        indexes = [
            models.Index(fields=['vehicle', 'start_date', 'end_date']),
        ]
        # extra constraints for the db
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gt=models.F('start_date')),
                name='end_date_after_start_date'
            ),

            # adding POSTGRES exclusion constraint for overlapping bookings
            ExclusionConstraint(
                name='exclude_overlapping_bookings',
                expressions=[
                    ('vehicle', '='),  # same vehicle
                    (
                        models.Func(
                            models.F('start_date'), 
                            models.F('end_date'), 
                            function='tstzrange', 
                            output_field=DateTimeRangeField()
                        ), 
                        '&&' # overlapping date ranges
                    )
                ],
            ),
        ]

    def __str__(self):
        return f"Booking {self.id} by {self.user} for {self.vehicle.make}"
