
import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from core.models import Agency
from vehicles.models import Vehicle

User = get_user_model()

def test_vehicles_api():
    print("\n=== Starting Vehicle API Tests ===")
    client = APIClient()

    # 1. Setup Agency & Admin
    print("\n--- Setting up Agency & Admin ---")
    email = 'agency_test@example.com'
    try:
        User.objects.get(email=email).delete()
    except User.DoesNotExist:
        pass
    
    admin_user = User.objects.create_user(
        username='agency_test_admin',
        email=email,
        password='Password123!',
        role='AGENCY_ADMIN',
        first_name='Admin',
        last_name='User'
    )
    
    agency = Agency.objects.create(
        user=admin_user,
        agency_name="Test Motors",
        contact_email="contact@testmotors.com",
        phone_number="555-0123"
    )
    
    # Authenticate
    client.force_authenticate(user=admin_user)
    print(f"Agency created: {agency.agency_name}")

    # 2. Setup Customer (for public view test)
    try:
        User.objects.get(username='customer_test').delete()
    except User.DoesNotExist:
        pass

    customer_user = User.objects.create_user(
        username='customer_test',
        email='cust@example.com',
        password='Password123!',
        role='CUSTOMER'
    )

    # 3. Test Create Vehicle (POST)
    print("\n--- Testing Create Vehicle (POST) ---")
    vehicle_data = {
        'make': 'Toyota',
        'model': 'Camry',
        'year': 2024,
        'vehicle_type': 'CAR',
        'daily_rental_rate': '50.00',
        'licence_plate': 'TEST-999',
        'status': 'AVAILABLE',
        # Simple specs (nested)
        'specs': {
            'transmission': 'AUTOMATIC',
            'fuel_type': 'HYBRID',
            'seats': 5,
            'is_air_conditioned': True
        }
        # Note: Specs handling depends on how DRF handles nested writes. 
        # By default ModelSerializer doesn't, we need to check if we implemented create() in serializer for specs.
        # Wait, the current VehicleDetailSerializer definition has read_only=True for specs!
        # So we can't create specs via the main endpoint unless we implemented nested write support.
        # Let's check serializer... it says "read_only=True" for specs.
        # This implies we can't create specs in the same request with the current code.
        # I'll try to create just the vehicle first.
    }
    
    # Adjusting data for read-only specs limitation
    # If the user wants nested creation, we need to update the serializer.
    # For now, let's test basic vehicle creation.
    data_no_specs = vehicle_data.copy()
    del data_no_specs['specs']

    response = client.post('/api/vehicles/', data_no_specs, format='json')
    
    if response.status_code == status.HTTP_201_CREATED:
        print("SUCCESS: Vehicle created.")
        slug = response.data['slug']
        print(f"Slug: {slug}")
        print(f"Owner Agency: {response.data.get('agency_name')}")
    else:
        print(f"FAILURE: {response.status_code}")
        print(response.data)
        return

    # 4. Test Get List (GET)
    print("\n--- Testing List View (GET) ---")
    client.logout() # public view
    response = client.get('/api/vehicles/')
    
    if response.status_code == status.HTTP_200_OK:
        print(f"SUCCESS: List retrieved. Count: {len(response.data)}")
    else:
        print(f"FAILURE: List retrieval failed. {response.status_code}")

    # 5. Test Get Detail (GET)
    print(f"\n--- Testing Detail View (GET) for slug: {slug} ---")
    response = client.get(f'/api/vehicles/{slug}/')
    
    if response.status_code == status.HTTP_200_OK:
        print("SUCCESS: Detail retrieved.")
    else:
        print(f"FAILURE: Detail retrieval failed. {response.status_code}")

    # Cleanup
    agency.delete()
    admin_user.delete()
    customer_user.delete()
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    try:
        test_vehicles_api()
    except Exception as e:
        print(f"An error occurred: {e}")
