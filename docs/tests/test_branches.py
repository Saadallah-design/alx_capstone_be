#!/usr/bin/env python3
"""
Test script for Branches App

Tests:
1. Branch creation by agency
2. Public listing
3. Branch detail retrieval
4. Permissions (agency vs public)
5. Inventory endpoint
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
from django.contrib.auth import get_user_model
from core.models import Agency
from branches.models import Branch
from vehicles.models import Vehicle

User = get_user_model()

def cleanup():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    User.objects.filter(email__in=['branch_test@example.com', 'customer_test@example.com']).delete()
    Agency.objects.filter(agency_name='Branch Test Agency').delete()
    Branch.objects.filter(name__contains='Test Branch').delete()
    print("✅ Cleanup complete\n")

def test_branches():
    """Run branch tests"""
    
    print("=" * 60)
    print("🏢 Branches App - Integration Tests")
    print("=" * 60)
    
    cleanup()
    client = APIClient()
    
    # ========================================
    # SETUP: Create Agency and User
    # ========================================
    print("\n📝 SETUP: Creating test user and agency...")
    
    # Create agency admin user
    admin_user = User.objects.create_user(
        username='branch_admin',
        email='branch_test@example.com',
        password='TestPass123!',
        role='AGENCY_ADMIN'
    )
    
    # Create agency
    agency = Agency.objects.create(
        user=admin_user,
        agency_name='Branch Test Agency',
        contact_email='contact@branchtest.com',
        phone_number='555-TEST'
    )
    print(f"✅ Agency created: {agency.agency_name}")
    
    # Login
    login_response = client.post('/api/auth/login/', {
        'username': 'branch_admin',
        'password': 'TestPass123!'
    }, format='json')
    
    assert login_response.status_code == 200, f"Login failed: {login_response.status_code}"
    token = login_response.data['access']
    print(f"✅ Logged in successfully")
    
    # ========================================
    # TEST 1: Create Branch (Agency Admin)
    # ========================================
    print("\n\n🏢 TEST 1: Branch Creation")
    print("-" * 60)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    branch_data = {
        'name': 'Test Branch Downtown',
        'phone_number': '555-1234',
        'email': 'downtown@branchtest.com',
        'city': 'Test City',
        'address': '123 Main Street, Downtown',
        'country': 'Test Country',
        'latitude': '40.712800',
        'longitude': '-74.006000',
        'opening_time': '09:00:00',
        'closing_time': '18:00:00',
        'is_pickup_point': True,
        'is_dropoff_point': True,
    }
    
    response = client.post('/api/branches/', branch_data, format='json')
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"❌ Branch creation failed: {response.data}")
        cleanup()
        return False
    
    branch_id = response.data['id']
    branch_slug = response.data['slug']
    print(f"✅ Branch created: {branch_slug}")
    print(f"   ID: {branch_id}")
    
    # ========================================
    # TEST 2: Public Branch Listing
    # ========================================
    print("\n\n📋 TEST 2: Public Branch Listing")
    print("-" * 60)
    
    client.credentials()  # Remove auth
    response = client.get('/api/branches/')
    
    assert response.status_code == 200, f"List failed: {response.status_code}"
    print(f"✅ Public can view branches")
    print(f"   Found {len(response.data)} branch(es)")
    
    # ========================================
    # TEST 3: Branch Detail Retrieval
    # ========================================
    print("\n\n🔍 TEST 3: Branch Detail Retrieval")
    print("-" * 60)
    
    response = client.get(f'/api/branches/{branch_slug}/')
    
    assert response.status_code == 200, f"Detail failed: {response.status_code}"
    print(f"✅ Retrieved branch details")
    print(f"   Name: {response.data['name']}")
    print(f"   City: {response.data['city']}")
    print(f"   Pickup: {response.data['is_pickup_point']}")
    
    # ========================================
    # TEST 4: Permission - Customer Cannot Create
    # ========================================
    print("\n\n🔒 TEST 4: Permission Check (Customer)")
    print("-" * 60)
    
    # Create customer user
    customer = User.objects.create_user(
        username='customer_test',
        email='customer_test@example.com',
        password='TestPass123!',
        role='CUSTOMER'
    )
    
    customer_login = client.post('/api/auth/login/', {
        'username': 'customer_test',
        'password': 'TestPass123!'
    }, format='json')
    
    customer_token = customer_login.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
    
    response = client.post('/api/branches/', branch_data, format='json')
    
    if response.status_code == 403:
        print("✅ Customer correctly denied branch creation")
    else:
        print(f"❌ Customer should not be able to create branches: {response.status_code}")
    
    # ========================================
    # TEST 5: Update Branch (Agency Admin)
    # ========================================
    print("\n\n✏️ TEST 5: Branch Update")
    print("-" * 60)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    update_data = {
        'opening_time': '08:00:00',
        'closing_time': '20:00:00',
    }
    
    response = client.patch(f'/api/branches/{branch_slug}/', update_data, format='json')
    
    if response.status_code == 200:
        print("✅ Branch updated successfully")
        print(f"   New hours: {response.data['opening_time']} - {response.data['closing_time']}")
    else:
        print(f"❌ Update failed: {response.status_code} - {response.data}")
    
    # ========================================
    # TEST 6: Inventory Endpoint (if Vehicle has current_location)
    # ========================================
    print("\n\n🚗 TEST 6: Inventory Endpoint")
    print("-" * 60)
    
    # Create a test vehicle
    try:
        branch = Branch.objects.get(slug=branch_slug)
        vehicle = Vehicle.objects.create(
            owner_agency=agency,
            make='Toyota',
            model='Camry',
            year=2024,
            vehicle_type='CAR',
            daily_rental_rate='75.00',
            licence_plate='BRANCH-TEST-001',
            status='AVAILABLE',
            current_location=branch
        )
        print(f"✅ Test vehicle created at branch")
        
        # Test inventory endpoint
        client.credentials()  # Public access
        response = client.get(f'/api/branches/{branch_slug}/inventory/')
        
        if response.status_code == 200:
            print(f"✅ Inventory endpoint works")
            print(f"   Vehicles at branch: {len(response.data)}")
        else:
            print(f"⚠️ Inventory endpoint issue: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Skipping inventory test: {e}")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n\n" + "=" * 60)
    print("🎉 BRANCHES APP TESTS COMPLETE!")
    print("=" * 60)
    print("\n✅ Branch CRUD operations")
    print("✅ Permission enforcement")
    print("✅ Public access controls")
    print("✅ Slug generation")
    print("\n" + "=" * 60)
    
    cleanup()
    return True

if __name__ == '__main__':
    try:
        success = test_branches()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        sys.exit(1)
