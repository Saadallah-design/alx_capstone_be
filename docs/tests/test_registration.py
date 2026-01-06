
import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.serializers import UserRegistrationSerializer

User = get_user_model()

def test_registration():
    print("--- Starting Registration Test ---")
    
    # Test Data
    test_data = {
        'username': 'testuser_123',
        'email': 'testuser123@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!'
    }
    
    # Clean up existing user if exists
    try:
        existing = User.objects.get(username=test_data['username'])
        print(f"Cleaning up existing user: {existing}")
        existing.delete()
    except User.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error cleaning up: {e}")

    try:
        existing_email = User.objects.get(email=test_data['email'])
        print(f"Cleaning up existing email: {existing_email}")
        existing_email.delete()
    except User.DoesNotExist:
        pass

    # Initialize Serializer
    serializer = UserRegistrationSerializer(data=test_data)
    
    if serializer.is_valid():
        print("Serializer is valid.")
        try:
            # Simulate what the view does: passing role='CUSTOMER'
            user = serializer.save(role='CUSTOMER')
            print(f"SUCCESS: User created successfully: {user.username} (ID: {user.id})")
            print(f"Role: {user.role}")
            print(f"Email: {user.email}")
            print(f"Agency: {user.agency}")
            
            # Verify Password Hashing
            if user.check_password(test_data['password']):
                print("Password check: PASS")
            else:
                print("Password check: FAIL")
                
        except Exception as e:
            print(f"FAILURE: Error saving user: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("FAILURE: Serializer is invalid.")
        print(serializer.errors)

if __name__ == '__main__':
    test_registration()
