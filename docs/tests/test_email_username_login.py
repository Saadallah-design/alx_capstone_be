#!/usr/bin/env python3
"""
Test script for Email/Username Login Functionality

Verifies that users can login with either:
1. Their username
2. Their email address
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

User = get_user_model()

def test_email_username_login():
    """Test that login works with both email and username"""
    
    print("\n" + "="*60)
    print("🔐 Testing Email/Username Login Functionality")
    print("="*60)
    
    client = APIClient()
    
    # Cleanup any existing test user
    User.objects.filter(username='test_user').delete()
    
    # Create test user
    print("\n1. Creating test user...")
    test_user = User.objects.create_user(
        username='test_user',
        email='testuser@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )
    print(f"✅ User created: username={test_user.username}, email={test_user.email}")
    
    # Test 1: Login with USERNAME
    print("\n2. Testing login with USERNAME...")
    response = client.post('/api/auth/login/', {
        'username': 'test_user',
        'password': 'TestPass123!'
    }, format='json')
    
    if response.status_code == status.HTTP_200_OK:
        print("✅ Login with USERNAME successful!")
        print(f"   Token: {response.data['access'][:30]}...")
        print(f"   User data: {response.data['user']}")
    else:
        print(f"❌ Login with USERNAME failed: {response.status_code}")
        print(f"   Error: {response.data}")
        return False
    
    # Test 2: Login with EMAIL
    print("\n3. Testing login with EMAIL...")
    response = client.post('/api/auth/login/', {
        'username': 'testuser@example.com',  # Email in username field
        'password': 'TestPass123!'
    }, format='json')
    
    if response.status_code == status.HTTP_200_OK:
        print("✅ Login with EMAIL successful!")
        print(f"   Token: {response.data['access'][:30]}...")
        print(f"   User data: {response.data['user']}")
    else:
        print(f"❌ Login with EMAIL failed: {response.status_code}")
        print(f"   Error: {response.data}")
        return False
    
    # Test 3: Invalid credentials
    print("\n4. Testing invalid credentials...")
    response = client.post('/api/auth/login/', {
        'username': 'test_user',
        'password': 'WrongPassword'
    }, format='json')
    
    if response.status_code == status.HTTP_401_UNAUTHORIZED or response.status_code == status.HTTP_400_BAD_REQUEST:
        print("✅ Invalid credentials correctly rejected")
    else:
        print(f"❌ Invalid credentials should have been rejected: {response.status_code}")
        return False
    
    # Test 4: Non-existent user
    print("\n5. Testing non-existent user...")
    response = client.post('/api/auth/login/', {
        'username': 'nonexistent@example.com',
        'password': 'Password123!'
    }, format='json')
    
    if response.status_code == status.HTTP_401_UNAUTHORIZED or response.status_code == status.HTTP_400_BAD_REQUEST:
        print("✅ Non-existent user correctly rejected")
    else:
        print(f"❌ Non-existent user should have been rejected: {response.status_code}")
        return False
    
    # Cleanup
    test_user.delete()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\n✅ Users can now login with either:")
    print("   - Username: 'test_user'")
    print("   - Email: 'testuser@example.com'")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == '__main__':
    try:
        success = test_email_username_login()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
