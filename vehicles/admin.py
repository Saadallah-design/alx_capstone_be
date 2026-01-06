from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle, VehicleSpecs, VehicleImage

# 1. adding inline vehicle specs 
class VehicleSpecsInline(admin.StackedInline):
    model = VehicleSpecs
    can_delete = False
    verbose_name_plural = 'Vehicle Specs'

# 2. Inline for vehicle image with preview
class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1 #this provides 1 empty slot for image upload
    readonly_fields = ('image_preview',)
    fields = ('image', 'is_main', 'image_preview')

    def image_preview(self, obj):
        # Check if object is saved and has an image
        if obj.pk and obj.image:
            try:
                # using the same Cloudinary transformation logic as get_thumbnail method
                thumb_url = obj.image.url.replace('/upload/', '/upload/w_100,h_100,c_fill,q_auto,f_auto/')
                return format_html('<img src="{}" style="border-radius: 5px; border: 1px solid #ccc;" />', thumb_url)
            except (AttributeError, ValueError):
                return "Preview unavailable"
        return "No Preview"
    
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'vehicle_type', 'owner_agency', 'status', 'daily_rental_rate')
    
    # Optimization: This fetches the Vehicle AND the Agency in ONE single database query.
    list_select_related = ('owner_agency',)
    
    # This brings both Specs and Images into the Vehicle edit page
    inlines = [VehicleSpecsInline, VehicleImageInline]

# admin.site.register(VehicleSpecs)
