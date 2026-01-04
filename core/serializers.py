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
        
        # Determine if we should auto-verify (MVP shortcut for admins/staff)
        is_verified = False
        if user.is_staff or user.role == 'AGENCY_ADMIN':
            is_verified = True
            
        agency = Agency.objects.create(
            user=user, 
            is_verified=is_verified,
            **validated_data
        )

        if is_verified:
            from django.utils import timezone
            agency.verification_date = timezone.now()
            agency.verification_note = "Auto-verified for administrative user."
            agency.save()
            
            # Ensure the user has the correct role to see the dashboard
            if user.role != 'AGENCY_ADMIN':
                user.role = 'AGENCY_ADMIN'
                user.save()
             
        return agency
