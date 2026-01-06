import json
from typing import Optional
from rest_framework import serializers
from .models import Vehicle, VehicleImage, VehicleSpecs
from drf_spectacular.utils import extend_schema_field

# creating serializers for vehicles app (mainly 4 serializers)

# handling image uploads and displays
class VehicleImageSerializer(serializers.ModelSerializer):
    # defining a thumbnail field for the image
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'is_main', 'thumbnail']

    def get_thumbnail(self, obj) -> Optional[str]:
        if not obj.image:
            return None
        url = obj.image.url
        return url.replace('/upload/', '/upload/w_400,h_300,c_fill,q_auto,f_auto/')



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
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None


# handling vehicle detail display
class VehicleDetailSerializer(serializers.ModelSerializer):
    # Now using nested serializers for related objects
    images = VehicleImageSerializer(many=True, required=False, read_only=True)
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
        Handle cases where 'specs' or 'images' are sent as stringified JSON or 
        nested multipart fields (common in multipart/form-data).
        """
        # Create a mutable copy if needed
        if hasattr(data, 'dict'):
            data = data.dict()
        elif isinstance(data, dict):
            data = data.copy()

        # 1. Handle specs stringified JSON
        if 'specs' in data and isinstance(data['specs'], str):
            try:
                data['specs'] = json.loads(data['specs'])
            except (ValueError, TypeError):
                pass
        
        # 2. Handle nested images in multipart (e.g., images[0]image, images[0]is_main)
        if any(key.startswith('images[') for key in data.keys()):
            images_dict = {}
            for key, value in data.items():
                if key.startswith('images['):
                    # extract index and field: images[0][image] -> 0, image
                    try:
                        import re
                        match = re.search(r'images\[(\d+)\](?:\[?(\w+)\]?)?', key)
                        if match:
                            index = int(match.group(1))
                            field = match.group(2) or 'image' # Default to image if only images[0]
                            
                            if index not in images_dict:
                                images_dict[index] = {}
                            
                            # Handle boolean strings for is_main
                            if field == 'is_main' and isinstance(value, str):
                                value = value.lower() == 'true'
                                
                            images_dict[index][field] = value
                    except (ValueError, IndexError, AttributeError):
                        continue
            
            if images_dict:
                # Convert dict to sorted list
                data['images'] = [images_dict[i] for i in sorted(images_dict.keys())]
                
        return super().to_internal_value(data)

    def create(self, validated_data):
        """
        Create a Vehicle, its related Specs, and its Images in a single request.
        """
        specs_data = validated_data.pop('specs', {})
        images_data = validated_data.pop('images', [])
        
        user = self.context['request'].user
        if not hasattr(user, 'agency'):
            raise serializers.ValidationError(
                {"detail": "You must be an agency user to create a vehicle."}
            )
            
        validated_data['owner_agency'] = user.agency
        
        # 1. Create the Vehicle
        vehicle = Vehicle.objects.create(**validated_data)
        
        # 2. Create Specs
        VehicleSpecs.objects.create(vehicle=vehicle, **specs_data)
        
        # 3. Create Images
        # If images were uploaded as files (e.g. via request.FILES), 
        # they might need special handling depending on how the frontend sends them.
        for index, image_data in enumerate(images_data):
            # The 'image_data' usually contains the file and 'is_main' bool
            VehicleImage.objects.create(vehicle=vehicle, **image_data)
            
        return vehicle

    def update(self, instance, validated_data):
        """
        Update a Vehicle, its related Specs, and optionally replace/add images.
        """
        specs_data = validated_data.pop('specs', {})
        images_data = validated_data.pop('images', None) # None means no update to images
        
        # Update core vehicle fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create nested specs
        if specs_data:
            VehicleSpecs.objects.update_or_create(
                vehicle=instance,
                defaults=specs_data
            )
            
        # Update images if provided
        if images_data is not None:
            # Simplest approach: Replace all images if a new set is provided
            # Or you could append. Given standard UI behavior, replacement or 
            # specific deletion is usually preferred.
            # Let's keep it simple: If new images are sent, we ADD them.
            for image_data in images_data:
                VehicleImage.objects.create(vehicle=instance, **image_data)
            
        return instance