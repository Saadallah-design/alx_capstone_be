from rest_framework import permissions


# This permissions is used for:  Customers shouldn't see other customers' bookings. 
# Agencies should only see bookings for their vehicles.
class IsBookingParticipant(permissions.BasePermission):
    """
    Allow access if user is:
    - The customer who made the booking
    - A member of the agency that owns the vehicle
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Customer who made the booking
        if obj.user == user:
            return True
        
        # Agency member (admin or staff)
        if user.is_agency_user() and user.agency == obj.agency:
            return True
        
        return False