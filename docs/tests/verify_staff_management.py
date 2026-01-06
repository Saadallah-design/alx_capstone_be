import os
import django

# =================================================================
# 1. DJANGO SETUP
# =================================================================
# We must set the DJANGO_SETTINGS_MODULE environment variable 
# so Django knows which settings file to use (DB config, apps, etc.).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')

# django.setup() initializes the apps and models.
# CRITICAL: This must be called BEFORE importing any DRF components
# because DRF checks settings (like REST_FRAMEWORK) at import time.
django.setup()

import json
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from core.models import Agency, AgencyMember
from core.views import AgencyStaffViewSet

# We use get_user_model() instead of 'from users.models import User'
# to ensure compatibility even if the Auth model changes in settings.
User = get_user_model()

def verify_staff_management():
    """
    This script acts as a 'Mini-Front End' to test the Staff Management logic.
    Instead of using a browser, we use APIRequestFactory to trigger the views directly.
    """
    print("--- Verifying Staff Management & Invitations ---")
    
    import time
    ts = int(time.time()) # Timestamp ensures unique data for every test run

    # -------------------------------------------------------------
    # SETUP: Create a Test Admin and a Test Agency
    # -------------------------------------------------------------
    admin_user, _ = User.objects.get_or_create(
        username=f'admin_{ts}', 
        email=f'admin_{ts}@test.com', 
        defaults={'role': 'AGENCY_ADMIN'}
    )
    admin_user.set_password('pass')
    admin_user.save()
    
    # Link the admin to an Agency profile
    agency, _ = Agency.objects.get_or_create(
        user=admin_user, 
        defaults={'agency_name': f'Agency_{ts}', 'is_verified': True}
    )
    
    # Create a 'Customer' who we will eventually invite to be Staff
    staff_user, _ = User.objects.get_or_create(
        username=f'staff_{ts}', 
        email=f'staff_{ts}@test.com', 
        defaults={'role': 'CUSTOMER'}
    )
    staff_user.set_password('pass')
    staff_user.save()

    # APIRequestFactory is a specialized tool for generating mock Request objects
    factory = APIRequestFactory()
    
    # -------------------------------------------------------------
    # TEST 1: INVITE STAFF (POST request)
    # -------------------------------------------------------------
    print("\n[TEST 1] Inviting staff by email...")
    # We target the 'create' action of our ViewSet
    view = AgencyStaffViewSet.as_view({'post': 'create'})
    
    data = {'email': f'staff_{ts}@test.com'}
    request = factory.post('/api/agencies/staff/', data, format='json')
    
    # force_authenticate bypasses the actual JWT login but acts as if 
    # the request came from the admin_user.
    force_authenticate(request, user=admin_user)
    
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("SUCCESS: Staff member invited/added.")
        staff_user.refresh_from_db() # Reload from DB to see the new Role
        print(f"Invite's new role: {staff_user.role}")
        if staff_user.role == 'AGENCY_STAFF':
            print("SUCCESS: Role updated to AGENCY_STAFF.")
        else:
            print("FAILURE: Role not updated.")
    else:
        print(f"FAILURE: Invite failed. Errors: {response.data}")
        return

    # -------------------------------------------------------------
    # TEST 2: LIST STAFF (GET request)
    # -------------------------------------------------------------
    print("\n[TEST 2] Listing staff members...")
    view_list = AgencyStaffViewSet.as_view({'get': 'list'})
    
    request_list = factory.get('/api/agencies/staff/')
    force_authenticate(request_list, user=admin_user)
    
    response_list = view_list(request_list)
    
    print(f"Status Code: {response_list.status_code}")
    if response_list.status_code == 200:
        print(f"Staff Count: {len(response_list.data)}")
        # Verify the user we just added is in the response data
        if any(m['email'] == f'staff_{ts}@test.com' for m in response_list.data):
            print("SUCCESS: Staff member found in list.")
        else:
            print("FAILURE: Staff member missing from list.")
    else:
        print("FAILURE: List failed.")

    # -------------------------------------------------------------
    # TEST 3: REMOVE STAFF (DELETE request)
    # -------------------------------------------------------------
    print("\n[TEST 3] Removing staff member...")
    membership_id = response.data['id']
    view_delete = AgencyStaffViewSet.as_view({'delete': 'destroy'})
    
    request_delete = factory.delete(f'/api/agencies/staff/{membership_id}/')
    force_authenticate(request_delete, user=admin_user)
    
    # ViewSets require the 'pk' argument for detail-level actions
    response_delete = view_delete(request_delete, pk=membership_id)
    
    print(f"Status Code: {response_delete.status_code}")
    if response_delete.status_code == 204:
        print("SUCCESS: Staff member removed.")
        staff_user.refresh_from_db()
        print(f"Staff member's current role: {staff_user.role}")
        if staff_user.role == 'CUSTOMER':
            print("SUCCESS: Role reset to CUSTOMER.")
        else:
            print("FAILURE: Role not reset.")
    else:
        print(f"FAILURE: Removal failed. Errors: {response_delete.data}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_staff_management()
