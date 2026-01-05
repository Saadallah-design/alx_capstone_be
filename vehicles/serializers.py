import json
from rest_framework import serializers
from .models import Vehicle, VehicleImage, VehicleSpecs
from drf_spectacular.utils import extend_schema_field

# creating serializers for vehicles app (mainly 4 serializers)

# handling image uploads and displays
class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'is_main']

# handling vehicle specs
class VehicleSpecsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleSpecs
        fields = ['id', 'transmission', 'fuel_type', 'seats', 'engine_capacity_cc', 'is_air_conditioned', 'is_helmet_included']

# handling vehicle list display: this one is light for search results
class VehicleListSerializer(serializers.ModelSerializer):
    # Add this to include the nested technical specs
    specs = VehicleSpecsSerializer(read_only=True)
    # Add this to include the full images array for frontend logic parity
    images = VehicleImageSerializer(many=True, read_only=True)
    
    # method to get just the main image thumbnail for list view
    main_image = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='current_location.name', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'slug', 'make', 'model', 'year', 'licence_plate', 
            'vehicle_type', 'daily_rental_rate', 'status', 'main_image', 
            'images', 'current_location', 'branch_name', 'specs'
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_main_image(self, obj):
        #  return the main image thumbnail
        first_image = obj.images.filter(is_main=True).first()
        if first_image:
            return first_image.image.url
        return None


# handling vehicle detail display
class VehicleDetailSerializer(serializers.ModelSerializer):
    # Now using nested serializers for related objects
    images = VehicleImageSerializer(many=True, read_only=True)
    # Changed from read_only=True to allow creation and updates
    specs = VehicleSpecsSerializer(required=True)
    agency_name = serializers.CharField(source='owner_agency.agency_name', read_only=True)
    branch_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner_agency', 'agency_name', 'make', 'model', 'year', 
            'vehicle_type', 'daily_rental_rate', 'licence_plate', 
            'status', 'slug', 'specs', 'images', 'created_at',
            'current_location', 'branch_details'
        ]
        read_only_fields = ['owner_agency', 'slug', 'branch_details']

    @extend_schema_field(serializers.DictField(child=serializers.CharField(), allow_null=True))
    def get_branch_details(self, obj):
        if obj.current_location:
            return {
                'name': obj.current_location.name,
                'slug': obj.current_location.slug,
                'city': obj.current_location.city
            }
        return None

    def to_internal_value(self, data):
        """
        Handle cases where 'specs' is sent as a stringified JSON (common in multipart/form-data).
        """
        if 'specs' in data and isinstance(data['specs'], str):
            try:
                # Create a mutable copy of the data if it's a QueryDict
                if hasattr(data, 'dict'):
                    data = data.dict()
                else:
                    data = data.copy()
                
                data['specs'] = json.loads(data['specs'])
            except (ValueError, TypeError):
                # If parsing fails, let the serializer handle the validation error
                pass
                
        return super().to_internal_value(data)

    def create(self, validated_data):
        """
        Create a Vehicle and its related Specs in a single request.
        """
        # Extract specs data with a default empty dict
        specs_data = validated_data.pop('specs', {})
        
        user = self.context['request'].user

        # Safety check: Ensuring the user actually owns an agency
        if not hasattr(user, 'agency'):
            raise serializers.ValidationError(
                {"detail": "You must be an agency user to create a vehicle."}
            )
            
        validated_data['owner_agency'] = user.agency
        
        # 1. Create the Vehicle first
        vehicle = Vehicle.objects.create(**validated_data)
        
        # 2. Create the child Specs linked to this vehicle
        VehicleSpecs.objects.create(vehicle=vehicle, **specs_data)
        
        return vehicle

    def update(self, instance, validated_data):
        """
        Update a Vehicle and its related Specs.
        """
        # Handle specs update if provided
        specs_data = validated_data.pop('specs', {})
        
        # Update the vehicle fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create nested specs
        if specs_data:
            VehicleSpecs.objects.update_or_create(
                vehicle=instance,
                defaults=specs_data
            )
            
        return instance