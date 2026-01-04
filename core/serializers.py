from rest_framework import serializers
from .models import Agency

class AgencyApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for customers to apply for an Agency account.
    """
    class Meta:
        model = Agency
        fields = ['agency_name', 'address', 'contact_email', 'phone_number', 'license_number', 'city']

    def create(self, validated_data):
        # Current user is the owner
        user = self.context['request'].user
        
        # Check if they already have an agency
        if hasattr(user, 'agency_profile'):
             raise serializers.ValidationError("You already have an agency application.")
             
        return Agency.objects.create(user=user, **validated_data)
