from django.contrib import admin
from .models import Vehicle, VehicleSpecs

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'vehicle_type', 'owner_agency', 'status', 'daily_rental_rate')

admin.site.register(VehicleSpecs)
