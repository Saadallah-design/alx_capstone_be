import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta, time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from users.models import User
from core.models import Agency
from branches.models import Branch
from vehicles.models import Vehicle
from rentals.models import Booking
from payments.models import Payment

def setup_test_data():
    print("--- Starting Test Data Setup ---")
    
    # 1. Create a Test Customer
    customer, created = User.objects.get_or_create(
        email='customer@example.com',
        defaults={
            'username': 'test_customer',
            'first_name': 'Test',
            'last_name': 'Customer',
        }
    )
    if created: print(f"Created Customer: {customer.email}")
    
    # 2. Create an Agency Admin
    admin_user, created = User.objects.get_or_create(
        email='agency_admin@example.com',
        defaults={
            'username': 'agency_admin',
            'first_name': 'Agency',
            'last_name': 'Admin',
        }
    )
    if created: print(f"Created Agency Admin User: {admin_user.email}")
    
    # 3. Create the Agency
    agency, created = Agency.objects.get_or_create(
        user=admin_user,
        defaults={
            'agency_name': 'Elite Phuket Rentals',
            'address': '123 Beach Road, Patong',
            'contact_email': 'info@eliterentals.com',
            'license_number': 'PHK-12345',
            'city': 'PATONG',
            'is_verified': True
        }
    )
    if created: print(f"Created Agency: {agency.agency_name}")

    # 4. Create a Branch
    branch, created = Branch.objects.get_or_create(
        name='Patong Beach Branch',
        agency=agency,
        defaults={
            'phone_number': '+66-123-4567',
            'email': 'patong@eliterentals.com',
            'city': 'Patong',
            'address': '45 Patong Beach St',
            'country': 'Thailand',
            'opening_time': time(8, 0),
            'closing_time': time(20, 0),
            'is_pickup_point': True,
            'is_dropoff_point': True
        }
    )
    if created: print(f"Created Branch: {branch.name}")

    # 5. Create a Vehicle
    from vehicles.models import VehicleSpecs
    vehicle, created = Vehicle.objects.get_or_create(
        licence_plate='TAX-999',
        owner_agency=agency,
        defaults={
            'make': 'Toyota',
            'model': 'Fortuner',
            'year': 2023,
            'daily_rental_rate': Decimal('1500.00'),
            'vehicle_type': 'CAR',
            'current_location': branch
        }
    )
    if created: 
        print(f"Created Vehicle: {vehicle.make} {vehicle.model}")
        VehicleSpecs.objects.create(
            vehicle=vehicle,
            transmission='AUTOMATIC',
            fuel_type='DIESEL',
            seats=7,
            is_air_conditioned=True
        )

    # 6. Create a Booking
    # Clear existing bookings and payments for this vehicle to avoid overlap validation and protected errors
    Payment.objects.filter(booking__vehicle=vehicle).delete()
    Booking.objects.filter(vehicle=vehicle).delete()
    
    start = timezone.now() + timedelta(days=2)
    end = start + timedelta(days=3)
    
    booking = Booking.objects.create(
        user=customer,
        vehicle=vehicle,
        agency=agency,
        pickup_location=branch,
        dropoff_location=branch,
        start_date=start,
        end_date=end,
        total_rental_cost=Decimal('4500.00'),
        booking_status='PENDING'
    )
    print(f"Created Booking ID: {booking.id}")

    # 7. Create a Payment Record for the Booking
    payment = Payment.objects.create(
        booking=booking,
        amount=booking.total_rental_cost,
        currency='THB',
        payment_type='RENTAL_FEE',
        status='PENDING',
        provider='Stripe',
        provider_transaction_id=f"pi_mock_{booking.id}" # Temporary mock ID
    )
    print(f"Created Payment UUID: {payment.uuid}")
    print(f"--- Setup Complete ---")
    
    print(f"\nTo test the Stripe session creation, run:")
    print(f"curl -X POST http://127.0.0.1:8000/payments/create-session/{payment.uuid}/")

if __name__ == "__main__":
    setup_test_data()
