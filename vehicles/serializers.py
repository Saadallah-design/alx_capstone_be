from rest_framework import serializers
from .models import Vehicle, VehicleImage, VehicleSpecs

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

    # method to get just the main image thumbnail for list view
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'daily_rental_rate', 'model', 'main_image']
    def get_main_image(self, obj):
        #  return the main image thumbnail
        first_image = obj.images.filter(is_main=True).first()
        if first_image:
            return first_image.image.url
        return None


# handling vehicle detail display
class VehicleDetailSerializer(serializers.ModelSerializer):
    #  now I must use nested serializers for related objects
    #  here im using related_name to access the related objects
    images = VehicleImageSerializer(many=True,read_only=True)
    specs = VehicleSpecsSerializer(read_only=True)
    agency_name = serializers.CharField(source='owner_agency.agency_name', read_only=True)
    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner_agency', 'agency_name', 'make', 'model', 'year', 
            'vehicle_type', 'daily_rental_rate', 'licence_plate', 
            'status', 'slug', 'specs', 'images', 'created_at'
        ]
        read_only_fields = ['owner_agency', 'slug']

    def create(self, validated_data):
        """
        Automatically assign the vehicle to the agency of the user creating it.
        """
        user = self.context['request'].user
        validated_data['owner_agency'] = user.agency
        return super().create(validated_data)