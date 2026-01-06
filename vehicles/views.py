from django.shortcuts import render
from django.db.models import Q
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
        user = self.request.user
        
        if self.request.method == 'GET':
            # 1. Platform Admins see everything
            if user.is_authenticated and user.is_platform_admin():
                return qs

            # 2. Check for explicit 'scope=agency' filter
            # This is used by the Dashboard to show "My Fleet" (only my agency's cars)
            scope = self.request.query_params.get('scope')
            if scope == 'agency' and user.is_authenticated and user.is_agency_user() and user.agency:
                return qs.filter(owner_agency=user.agency)

            # 3. Default: Public/Search View
            # Everyone (including agency staff looking to rent) sees all AVAILABLE vehicles

            # 3. Public/Customers only see AVAILABLE vehicles
            return qs.filter(status='AVAILABLE')
        
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

    # SIDENOTE: 
    #  using both get_queryset and get_permissions is used for two different purposes
    #  VISIBILITY: get_queryset is used to limit what records the view can even "see"
    #  AUTHORIZATION: get_permissions is used to limit what actions the user can perform on the records

    def get_queryset(self):
        """
        The 'Wall of Defense': Limits what records the view can even "see".
        """
        # the select related handles one-to-one/foreign keys
        # now I will add prefetch which handles many-to-many/foreign keys
        qs = Vehicle.objects.select_related('owner_agency', 'specs').prefetch_related('images').all()
        
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
