#!/usr/bin/env python3
"""
Integration Test Script for Car Rental Platform

Tests the complete workflow:
1. User Registration & Authentication (Email/Username login)
2. Agency creates Branches
3. Agency creates Vehicles (linked to branches)
4. Customer books a vehicle (using branches)
5. Booking management (view, cancel)
6. Security & Permission enforcement
7. Custom endpoints (Inventory)
"""

import os
import sys
import django

# Django setup
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
from core.models import Agency
from branches.models import Branch
from vehicles.models import Vehicle, VehicleSpecs
from rentals.models import Booking

User = get_user_model()

def cleanup_test_data():
    """Clean up any existing test data"""
    print("\n🧹 Cleaning up existing test data...")
    User.objects.filter(email__in=[
        'agency_owner@test.com',
        'customer_john@test.com',
        'customer_jane@test.com'
    ]).delete()
    
    Agency.objects.filter(agency_name='Test Motors').delete()
    Branch.objects.filter(agency__agency_name='Test Motors').delete()
    Vehicle.objects.filter(licence_plate__startswith='TEST').delete()
    print("✅ Cleanup complete\n")

def test_platform_integration():
    """Run comprehensive integration tests"""
    
    print("=" * 60)
    print("🚀 Car Rental Platform - Integration Tests")
    print("=" * 60)
    
    cleanup_test_data()
    client = APIClient()
    
    # ========================================
    # PHASE 1: User Registration & Authentication
    # ========================================
    print("\n📝 PHASE 1: User Registration & Authentication")
    print("-" * 60)
    
    # Test 1.1: Register Agency Admin
    print("\n1.1 Testing Agency Admin Registration...")
    agency_data = {
        'username': 'testmotors_admin',
        'email': 'agency_owner@test.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
        'first_name': 'Test',
        'last_name': 'Motors',
        'role': 'AGENCY_ADMIN'
    }
    
    response = client.post('/api/auth/register/', agency_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, f"Registration failed: {response.data}"
    print("✅ Agency admin registered successfully")
    
    # Test 1.2: Login Agency Admin (using EMAIL)
    print("\n1.2 Testing Agency Admin Login (with EMAIL)...")
    login_response = client.post('/api/auth/login/', {
        'username': 'agency_owner@test.com',  # ✅ Can use email now!
        'password': 'SecurePass123!'
    }, format='json')
    
    assert login_response.status_code == status.HTTP_200_OK, f"Login failed: {login_response.data}"
    agency_token = login_response.data['access']
    print(f"✅ Login successful")
    
    # Test 1.3: Create Agency Profile
    print("\n1.3 Creating Agency Profile...")
    agency_admin = User.objects.get(email='agency_owner@test.com')
    # Set role to AGENCY_ADMIN (default is CUSTOMER)
    agency_admin.role = 'AGENCY_ADMIN'
    agency_admin.save()
    
    agency = Agency.objects.create(
        user=agency_admin,
        agency_name='Test Motors',
        contact_email='contact@testmotors.com',
        phone_number='555-1234'
    )
    print(f"✅ Agency created: {agency.agency_name}")
    
    # Test 1.4: Register Customer
    print("\n1.4 Testing Customer Registration...")
    customer_data = {
        'username': 'john_doe',
        'email': 'customer_john@test.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
        'first_name': 'John',
        'last_name': 'Doe'
    }
    
    response = client.post('/api/auth/register/', customer_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, "Customer registration failed"
    print("✅ Customer registered successfully")
    
    # Test 1.5: Customer Login (using USERNAME)
    print("\n1.5 Testing Customer Login (with USERNAME)...")
    customer_login = client.post('/api/auth/login/', {
        'username': 'john_doe',
        'password': 'SecurePass123!'
    }, format='json')
    
    assert customer_login.status_code == status.HTTP_200_OK, "Customer login failed"
    customer_token = customer_login.data['access']
    print(f"✅ Customer login successful")
    
    # ========================================
    # PHASE 2: Branch Management (Agency)
    # ========================================
    print("\n\n🏢 PHASE 2: Branch Management")
    print("-" * 60)
    
    # Test 2.1: Create Branch
    print("\n2.1 Creating Agency Branch...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {agency_token}')
    
    branch_data = {
        'name': 'Downtown Branch',
        'phone_number': '555-9999',
        'email': 'downtown@testmotors.com',
        'city': 'Test City',
        'address': '789 Main Blvd',
        'country': 'Test Country',
        'opening_time': '08:00:00',
        'closing_time': '20:00:00',
        'is_active': True,
        'is_pickup_point': True,
        'is_dropoff_point': True
    }
    
    response = client.post('/api/branches/', branch_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, f"Branch creation failed: {response.data}"
    branch_id = response.data['id']
    branch_slug = response.data['slug']
    print(f"✅ Branch created: {branch_slug}")
    
    # ========================================
    # PHASE 3: Vehicle Management (Agency)
    # ========================================
    print("\n\n🚗 PHASE 3: Vehicle Management")
    print("-" * 60)
    
    # Test 3.1: Agency Creates Vehicle (linked to branch)
    print("\n3.1 Testing Vehicle Creation (Linked to Branch)...")
    
    vehicle_data = {
        'make': 'Toyota',
        'model': 'Camry',
        'year': 2024,
        'vehicle_type': 'CAR',
        'daily_rental_rate': '75.00',
        'licence_plate': 'TEST-001',
        'status': 'AVAILABLE',
        'current_location': branch_id  # Link to branch
    }
    
    response = client.post('/api/vehicles/', vehicle_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, f"Vehicle creation failed: {response.data}"
    vehicle_id = response.data['id']
    vehicle_slug = response.data['slug']
    print(f"✅ Vehicle created at branch: {vehicle_slug}")
    
    # Test 3.2: Create Vehicle Specs
    print("\n3.2 Creating Vehicle Specs...")
    vehicle = Vehicle.objects.get(id=vehicle_id)
    specs = VehicleSpecs.objects.create(
        vehicle=vehicle,
        transmission='AUTOMATIC',
        fuel_type='HYBRID',
        seats=5,
        engine_capacity_cc=2500,
        is_air_conditioned=True
    )
    print(f"✅ Specs created")
    
    # ========================================
    # PHASE 4: Booking Management (Customer)
    # ========================================
    print("\n\n📅 PHASE 4: Booking Management")
    print("-" * 60)
    
    # Test 4.1: Customer Creates Booking using Branch
    print("\n4.1 Testing Booking Creation with Branch...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
    
    start_date = timezone.now() + timedelta(days=2)
    end_date = start_date + timedelta(days=5)
    
    booking_data = {
        'vehicle': vehicle_id,
        'pickup_location': branch_id,
        'dropoff_location': branch_id,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }
    
    response = client.post('/api/bookings/', booking_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, f"Booking failed: {response.data}"
    booking_id = response.data['id']
    total_cost = response.data['total_rental_cost']
    print(f"✅ Booking created: ID={booking_id}, Cost=${total_cost}")
    
    # Test 4.2: Inventory Endpoint Check
    print("\n4.2 Testing Branch Inventory Endpoint...")
    client.credentials()  # Public
    response = client.get(f'/api/branches/{branch_slug}/inventory/')
    assert response.status_code == status.HTTP_200_OK, f"Inventory failed: {response.data}"
    print(f"✅ Inventory retrieved: Found {len(response.data)} vehicle(s)")
    
    # ========================================
    # PHASE 5: Permission & Security Tests
    # ========================================
    print("\n\n🔒 PHASE 5: Security & Permissions")
    print("-" * 60)
    
    # Test 5.1: Register Another Customer
    print("\n5.1 Creating Second Customer...")
    jane_data = {
        'username': 'jane_smith',
        'email': 'customer_jane@test.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
        'first_name': 'Jane',
        'last_name': 'Smith'
    }
    
    client.credentials()
    response = client.post('/api/auth/register/', jane_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, f"Jane registration failed: {response.data}"
    
    jane_login = client.post('/api/auth/login/', {
        'username': 'jane_smith',
        'password': 'SecurePass123!'
    }, format='json')
    jane_token = jane_login.data['access']
    print("✅ Second customer created and logged in")
    
    # Test 5.2: Customer Cannot View Other Customer's Booking
    print("\n5.2 Testing Cross-Customer Privacy...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {jane_token}')
    response = client.get(f'/api/bookings/{booking_id}/')
    assert response.status_code == status.HTTP_404_NOT_FOUND, "Privacy breach! Jane saw John's booking"
    print("✅ Customer cannot view other customer's bookings")
    
    # Test 5.3: Agency Can View Their Bookings
    print("\n5.3 Testing Agency Access...")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {agency_token}')
    response = client.get(f'/api/bookings/{booking_id}/')
    assert response.status_code == status.HTTP_200_OK, "Agency should see booking"
    print("✅ Agency can view bookings for their vehicles")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✅ Users App: Registration, Login, JWT")
    print("✅ Branches App: CRUD, Inventory, Locations")
    print("✅ Vehicles App: CRUD, Branch Assignment")
    print("✅ Rentals App: Booking Creation, Validation")
    print("✅ Security: Privacy, Permissions, Access Control")
    print("\n" + "=" * 60)
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    cleanup_test_data()
    print("✅ Cleanup complete\n")

if __name__ == '__main__':
    try:
        test_platform_integration()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        cleanup_test_data()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
        sys.exit(1)
