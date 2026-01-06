
import os
import django
import sys
# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIRequestFactory

from django.contrib.auth import get_user_model
from users.serializers import CustomTokenObtainPairSerializer, UserProfileDetailSerializer
from core.models import Agency

User = get_user_model()

def test_user_flow():
    print("\n=== Starting User Flow Test (Login & Profile) ===")

    # 1. Setup Test User
    email = 'flowtest@example.com'
    password = 'TestPassword123!'
    username = 'flowtest_user'
    
    try:
        user = User.objects.get(email=email)
        print(f"Found existing user {username}, deleting...")
        user.delete()
    except User.DoesNotExist:
        pass

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Flow',
        last_name='Tester'
    )
    print(f"Created user: {user.username} (ID: {user.id})")

    # 2. Test Login (Token Generation)
    print("\n--- Testing Login (Token Serializer) ---")
    
    # We need to simulate the serializer receiving data
    login_data = {'email': email, 'password': password} # Serializer expects credentials but we can just pass user object to get_token
    
    # SimpleJWT's TokenObtainPairSerializer usually takes credentials in `validate`, 
    # but here we can directly test the custom `get_token` class method and the `validate` method.
    
    # Test Custom Claims in Token
    token = CustomTokenObtainPairSerializer.get_token(user)
    access_token = token.access_token
    
    print(f"Token Generated. Claims:")
    print(f" - role: {access_token.get('role')}")
    print(f" - agency_id: {access_token.get('agency_id')}")
    
    # Verify claims
    if access_token['role'] == 'CUSTOMER' and access_token['agency_id'] is None:
        print("SUCCESS: Token claims are correct for Customer.")
    else:
        print("FAILURE: Token claims incorrect.")

    # Test Response Data (validate method)
    # We need to instantiate the serializer with data to call validate()
    # Note: TokenObtainPairSerializer depends on authenticate(), so we might need a Request context or mock it.
    # A simpler way is to check the `get_token` logic we just did, and trust `validate` calls it.
    # Let's try to verify the `validate` response structure if possible, but it requires a valid request.
    
    # 3. Test Profile Serializer
    print("\n--- Testing Profile Serializer (Me Endpoint) ---")
    profile_serializer = UserProfileDetailSerializer(user)
    data = profile_serializer.data
    
    print("Profile Data keys:", data.keys())
    print(f" - Agency field: {data.get('agency')}")
    print(f" - Role display: {data.get('role_display')}")
    
    if data['username'] == username and data['agency'] is None:
        print("SUCCESS: Profile serialized correctly for Customer.")
    else:
        print("FAILURE: Profile data mismatch.")

    # 4. Test Agency Admin Flow
    print("\n--- Testing Agency Admin Flow ---")
    
    # Promote user to Agency Admin and create dummy agency
    user.role = 'AGENCY_ADMIN'
    user.save()
    
    agency = Agency.objects.create(
        user=user,
        agency_name="Test Agency",
        contact_email="agency@test.com",
        phone_number="1234567890"
    )
    user.refresh_from_db() # Reload relations
    print(f"Promoted user to AGENCY_ADMIN and created agency: {agency.agency_name}")

    # Re-test Token Claims
    token = CustomTokenObtainPairSerializer.get_token(user)
    access_token = token.access_token
    print(f"New Token Claims:")
    print(f" - role: {access_token.get('role')}")
    print(f" - agency_id: {access_token.get('agency_id')}")

    if access_token['agency_id'] == agency.id:
        print("SUCCESS: Token now contains correct agency_id.")
    else:
        print(f"FAILURE: Expected agency_id {agency.id}, got {access_token.get('agency_id')}")

    # Re-test Profile Serializer
    profile_serializer = UserProfileDetailSerializer(user)
    data = profile_serializer.data
    
    agency_data = data.get('agency')
    if agency_data and agency_data['agency_name'] == "Test Agency":
        print("SUCCESS: Profile now includes Agency details.")
    else:
        print(f"FAILURE: Profile missing agency details. Got: {agency_data}")

    # Cleanup
    agency.delete()
    user.delete()
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_user_flow()
