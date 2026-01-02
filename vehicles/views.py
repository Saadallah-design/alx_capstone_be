from django.shortcuts import render
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle
from .serializers import VehicleListSerializer, VehicleDetailSerializer
from .permissions import IsAgencyAdminOrStaff, IsOwnerAgency

#  for permissions it is defined in the permissions.py

# Vehicle List & Create View
# GET: List all vehicles (Public - filtered by status='AVAILABLE' by default)
# POST: Create new vehicle (Agency Admin/Staff only)
class VehicleListCreateView(generics.ListCreateAPIView):
    # This query is optimized by using select_related to fetch related objects in a single query
    queryset = Vehicle.objects.select_related('owner_agency','specs').all()
    
    # Filter backends for search and filtering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Fields available for filtering (must use double __ to access it since they re nested)
    filterset_fields = ['status', 'vehicle_type', 'specs__transmission', 'specs__fuel_type', 'year']
    
    # Fields available for text search
    search_fields = ['make', 'model', 'vehicle_type']
    
    # Default ordering
    ordering_fields = ['daily_rental_rate', 'year', 'created_at']
    ordering = ['-created_at']


    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == 'GET':
            # Agency users (Admins & Staff) should see all their vehicles (Rented, Maintenance, etc.)
            # Public users should only see AVAILABLE vehicles.
            if not (self.request.user.is_authenticated and self.request.user.is_agency_user()):
                return qs.filter(status='AVAILABLE')

            # Note: Theoretically, we might want to filter this further to only show 
            # *their* agency's vehicles if they are logged in, but for a "Marketplace" list,
            # seeing all cars might be intended. 
            # However, usually, a LIST view for admins implies managing THEIR fleet.
            # If this is a global marketplace, seeing all is fine.
            # Given the context, let's keep it as returning all (but unfiltered by status)
            # strictly for agency users, or add permission-based filtering later if needed.
            return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VehicleDetailSerializer # Use detailed serializer for creation to handle all fields
        return VehicleListSerializer # Lightweight serializer for listing

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAgencyAdminOrStaff()]
        return [permissions.AllowAny()] # Public listing

    # perform_create removed: Logic is handled in VehicleDetailSerializer.create()


# Vehicle Detail View
# GET: Retrieve detail (Public)
# PUT/PATCH: Update vehicle (Owner Agency only)
# DELETE: Remove vehicle (Owner Agency only)
class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleDetailSerializer
    lookup_field = 'slug' # Using slug for SEO friendly URLs

    def get_queryset(self):
        """
        The 'Wall of Defense': Limits what records the view can even "see".
        """
        qs = Vehicle.objects.select_related('owner_agency', 'specs').all()
        
        # Check if the user is trying to change data (Write operations)
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Security: Only return vehicles that BELONG to the user's agency.
            if self.request.user.is_authenticated and self.request.user.agency:
                return qs.filter(owner_agency=self.request.user.agency)
            
            # If a random person tries to DELETE, return an empty set (404 Not Found).
            return qs.none() 
            
        return qs # Public can retrieve (GET) any vehicle by slug.

    

    def get_permissions(self):
        """
        This is the 'Key to the Gate': Checks if the user has the right credentials.
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # 1. Must be logged in.
            # 2. IsOwnerAgency verifies user.agency == vehicle.owner_agency.
            return [permissions.IsAuthenticated(), IsOwnerAgency()]
        return [permissions.AllowAny()] # Public read access
