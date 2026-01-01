from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle', 'agency', 'start_date', 'end_date', 'booking_status', 'total_rental_cost')
    list_filter = ('booking_status', 'start_date')
