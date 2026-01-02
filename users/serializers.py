# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model


from django.contrib.auth.password_validation import validate_password

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