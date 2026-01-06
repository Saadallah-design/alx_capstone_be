import os
import django
# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from rest_framework.test import APIClient
from django.urls import reverse
from users.models import User
from core.models import Agency

def test_agency_flow():
    client = APIClient()
    
    # 1. Create a customer
    print("\n--- Phase 1: Registration ---")
    user = User.objects.create_user(
        username="applicant_01",
        email="applicant@example.com",
        password="password123",
        role="CUSTOMER"
    )
    client.force_authenticate(user=user)
    print(f"✅ Registered customer: {user.username}")

    # 2. Check initial profile status
    print("\n--- Phase 2: Initial Profile Status ---")
    response = client.get('/api/auth/me/')
    data = response.json()
    print(f"   is_approved: {data.get('is_approved')}")
    print(f"   is_pending_agency: {data.get('is_pending_agency')}")

    # 3. Apply for Agency
    print("\n--- Phase 3: Agency Application ---")
    app_data = {
        "agency_name": "Applicant Motors",
        "address": "123 Test St",
        "contact_email": "admin@applicant.com",
        "phone_number": "123456789",
        "license_number": "LIC-999",
        "city": "PATONG"
    }
    response = client.post('/api/core/agencies/apply/', app_data)
    print(f"✅ Response Status: {response.status_code}")
    print(f"✅ Message: {response.json().get('message')}")

    # 4. Check status after application
    print("\n--- Phase 4: Post-Application Status ---")
    response = client.get('/api/auth/me/')
    data = response.json()
    print(f"   is_approved: {data.get('is_approved')} (Expect: False)")
    print(f"   is_pending_agency: {data.get('is_pending_agency')} (Expect: True)")

    # 5. Simulate Admin Verification
    print("\n--- Phase 5: Admin Verification Simulation ---")
    agency = Agency.objects.get(agency_name="Applicant Motors")
    agency.is_verified = True
    agency.save()
    user.role = 'AGENCY_ADMIN'
    user.save()
    print("✅ Admin verified agency and upgraded user role")

    # 6. Final Status Check
    print("\n--- Phase 6: Final Verification Check ---")
    response = client.get('/api/auth/me/')
    data = response.json()
    print(f"   is_approved: {data.get('is_approved')} (Expect: True)")
    print(f"   is_pending_agency: {data.get('is_pending_agency')} (Expect: False)")

if __name__ == "__main__":
    try:
        test_agency_flow()
    finally:
        # Cleanup
        User.objects.filter(username="applicant_01").delete()
        print("\n🧹 Cleanup complete")
