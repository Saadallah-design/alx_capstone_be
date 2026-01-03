from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from vehicles.serializers import VehicleListSerializer
from users.serializers import UserProfileDetailSerializer

class BookingListSerializer(serializers.ModelSerializer):
    vehicle_make = serializers.CharField(source='vehicle.make', read_only=True)
    vehicle_model = serializers.CharField(source='vehicle.model', read_only=True)
    vehicle_image = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'vehicle',
            'vehicle_make',
            'vehicle_model',
            'vehicle_image',
            'start_date',
            'end_date',
            'total_rental_cost',
            'booking_status',
        ]
    
    def get_vehicle_image(self, obj):
        # Return the main image thumbnail
        first_image = obj.vehicle.images.filter(is_main=True).first()
        if first_image:
            return first_image.image.url
        return None


class BookingDetailSerializer(serializers.ModelSerializer):
    vehicle = VehicleListSerializer(read_only=True)
    user = UserProfileDetailSerializer(read_only=True)
    agency_name = serializers.CharField(source='agency.agency_name', read_only=True)
    pickup_branch_name = serializers.CharField(source='pickup_location.name', read_only=True)
    dropoff_branch_name = serializers.CharField(source='dropoff_location.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'agency', 'vehicle', 'pickup_location', 'dropoff_location',
            'start_date', 'end_date', 'total_rental_cost', 'booking_status',
            'agency_name', 'pickup_branch_name', 'dropoff_branch_name'
        ]
        read_only_fields = ['total_rental_cost']


# Booking Create Serializer
class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'vehicle', 'pickup_location', 'dropoff_location',
            'start_date', 'end_date', 'total_rental_cost', 'booking_status'
        ]
        read_only_fields = ['id', 'total_rental_cost', 'booking_status']
    
    def validate(self, data):
        # 1. Validate start_date is not in the past
        if data['start_date'] < timezone.now():
            raise serializers.ValidationError("Sorry: Start date cannot be in the past.")
        
        # 2. Validate date range
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("Sorry: End date must be after start date.")
        
        # 3. Check vehicle availability (overlap check)
        # Note: Model's clean() will also catch this, but early validation helps UX
        overlapping = Booking.objects.filter(
            vehicle=data['vehicle'],
            start_date__lt=data['end_date'],
            end_date__gt=data['start_date']
        ).exclude(booking_status='CANCELLED')
        
        if overlapping.exists():
            raise serializers.ValidationError(
                "Sorry: This vehicle is not available for the selected dates."
            )
        
        return data
    
    def create(self, validated_data):
        # Auto-assign user from request context
        user = self.context['request'].user
        
        # Auto-assign agency from vehicle's owner
        vehicle = validated_data['vehicle']
        agency = vehicle.owner_agency
        
        # Create booking
        booking = Booking.objects.create(
            user=user,
            agency=agency,
            **validated_data
        )
        return booking