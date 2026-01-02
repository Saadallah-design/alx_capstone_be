from django.urls import path
from .views import BookingListCreateView, BookingDetailView, AgencyBookingListView


app_name = 'rentals'

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('agency/', AgencyBookingListView.as_view(), name='agency-bookings'),  # Optional
]