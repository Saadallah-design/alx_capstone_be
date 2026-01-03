from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingListSerializer, BookingCreateSerializer, BookingDetailSerializer
from .permissions import IsBookingParticipant
from vehicles.permissions import IsAgencyAdminOrStaff


# Booking List & Create View
class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Customers see only their own bookings
        # Agency users see bookings for their agency's vehicles
        user = self.request.user
        if user.is_customer():
            return Booking.objects.filter(user=user).order_by('-start_date')
        elif user.is_agency_user():
            return Booking.objects.filter(agency=user.agency).order_by('-start_date')
        return Booking.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer


class BookingDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingParticipant]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_customer():
            return Booking.objects.filter(user=user)
        elif user.is_agency_user():
            return Booking.objects.filter(agency=user.agency)
        return Booking.objects.none()
    
    def update(self, request, *args, **kwargs):
        # Only allow status updates (e.g., cancellation)
        # Prevent changing dates/vehicle after booking
        booking = self.get_object()
        
        # Customers can only cancel
        if request.user.is_customer():
            if 'booking_status' in request.data:
                if request.data['booking_status'] != 'CANCELLED':
                    return Response(
                        {"error": "Customers can only cancel bookings."},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        return super().update(request, *args, **kwargs)


# Agency dashboard to see all bookings for their vehicles
class AgencyBookingListView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgencyAdminOrStaff]
    
    def get_queryset(self):
        agency = self.request.user.agency
        return Booking.objects.filter(agency=agency).order_by('-start_date')