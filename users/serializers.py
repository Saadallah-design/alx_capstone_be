# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from core.models import Agency
from drf_spectacular.utils import extend_schema_field

User = get_user_model()
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        # this is the logic for password confirmation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields do not match.")
        return attrs
    
    def create(self, validated_data):
        # before saving to the db, lets first remove the comfirmation field
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            # role='CUSTOMER' # Default role already in the views
        )
        return user


# userSerializer to display user details
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class AgencyBasicSerializer(serializers.ModelSerializer):
    """
    Basic agency info for nested display in user profile.
    Only shows essential read-only information.
    """
    class Meta:
        model = Agency
        fields = ['id', 'agency_name', 'contact_email', 'phone_number']
        read_only_fields = ['id', 'agency_name', 'contact_email', 'phone_number']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile retrieval and updates.
    
    Features:
    - Shows agency details (nested, read-only)
    - Allows updating personal info
    - Prevents users from changing their own role
    - Includes helpful computed fields
    """

    # Nested agency information (read-only)
    agency = AgencyBasicSerializer(read_only=True)
    
    # Computed fields (not in database, generated on-the-fly)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_approved = serializers.SerializerMethodField()
    is_pending_agency = serializers.SerializerMethodField()
    


    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 

            'role', 
            'agency',

            'date_joined',
            'phone_number',

            'is_approved',
            'is_pending_agency',
            ]

        # Fields that cannot be changed via profile update
        read_only_fields = [
            'id',
            'email',          # Email changes require verification (separate endpoint)
            'username',       # Username is permanent
            'date_joined',
            'role',           # Role changes require admin action
            'agency',         # Agency assignment requires admin action
        ]

    def get_can_manage_agency(self, obj):
        """
        Check if user has agency management permissions.
        Used by frontend to show/hide certain UI elements.
        """
        return obj.is_agency_admin() or obj.is_platform_admin()

    def validate_phone_number(self, value):
        """Custom validation for phone number format"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits, spaces, + and -")
        return value

    @extend_schema_field(serializers.BooleanField())
    def get_is_approved(self, obj):
        """Account is fully verified and role is Agency Admin"""
        if obj.is_agency_admin():
            # If they are an admin, they are approved
            return True
        # If they are a customer but their agency profile is verified (waiting for role swap)
        agency = obj.agency
        return agency.is_verified if agency else False

    @extend_schema_field(serializers.BooleanField())
    def get_is_pending_agency(self, obj):
        """Has an agency profile but is still a Customer (pending review)"""
        # If they are a customer but have a linked agency profile
        has_agency = hasattr(obj, 'agency_profile') and obj.agency_profile is not None
        if obj.is_customer() and has_agency:
            return not obj.agency_profile.is_verified
        return False

    def update(self, instance, validated_data):
        """
        Override update to add custom logic when profile is updated.
        
        Example use cases:
        - Log profile changes
        - Send notification email
        - Trigger webhook
        """
        # Update the user instance
        instance = super().update(instance, validated_data)
        
        # Optional: Add audit logging
        # AuditLog.objects.create(
        #     user=instance,
        #     action='profile_updated',
        #     changes=validated_data
        # )
        
        return instance


class UserProfileDetailSerializer(UserProfileSerializer):
    """
    Extended serializer with more details for the user's own profile.
    Includes additional fields that other users shouldn't see.
    """
    
    # Statistics about user's activity
    total_rentals = serializers.SerializerMethodField()
    active_rentals = serializers.SerializerMethodField()
    
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + [
            'total_rentals',
            'active_rentals',
            'is_active',
        ]
    

    @extend_schema_field(serializers.IntegerField())
    def get_total_rentals(self, obj):
        """Count of all rentals made by this user"""
        return obj.bookings.count()  # Using correct related_name 'bookings'
    
    @extend_schema_field(serializers.IntegerField())
    def get_active_rentals(self, obj):
        """Count of currently active rentals"""
        from django.utils import timezone
        # Assuming 'CONFIRMED' status and current date within range
        return obj.bookings.filter(
            end_date__gte=timezone.now(),
            booking_status='CONFIRMED'
        ).count()



# adding jwt custom claims serializer for efficient user role checks and db queries

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that:
    1. Accepts email OR username for login
    2. Adds custom claims to the JWT token
    """
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False
    
    @classmethod
    def get_token(cls, user):
        """Override to add custom claims to the token"""
        token = super().get_token(user)

        # adding custom claims to the token (DECODED ACCESS TOKEN PAYLOAD)
        token['role'] = user.role
        token['id'] = user.id

        if user.agency:
            token['agency_id'] = user.agency.id
        else:
            token['agency_id'] = None

        return token

    def validate(self, attrs):
        """
        Merge of: 
        1. Custom authentication (Allows email OR username)
        2. Custom response structure (Adds user/agency info to the response)
        """
        # Support both 'username' and 'email' as keys from the frontend
        username_or_email = attrs.get('username') or attrs.get('email')
        password = attrs.get('password')
        
        from django.contrib.auth import authenticate
        
        user = authenticate(
            request=self.context.get('request'),
            username=username_or_email,
            password=password
        )
        
        if user is None:
            raise serializers.ValidationError(
                'No active account found with the given credentials'
            )
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        # Manually trigger token generation
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        # Add extra user information to the response (UI personalization)
        data['user'] = {
            'role': user.role,
            'id': user.id, 
            'full_name': user.username,
            'email': user.email,
            'permissions': {
                'is_customer': user.is_customer(),
                'is_agency_admin': user.is_agency_admin(),
                'is_agency_staff': user.is_agency_staff(),
                'is_platform_admin': user.is_platform_admin(),
            }
        }

        # Check if agency exists to avoid 'NoneType' attribute errors
        if user.agency:
            data['agency'] = {
                'id': user.agency.id,
                'name': user.agency.agency_name,
                'slug': getattr(user.agency, 'slug', None)
            }
        else:
            data['agency'] = None

        return data

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Password fields do not match."})
        return attrs
