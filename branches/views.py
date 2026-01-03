# will use ModelViewSet

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Branch
from .serializers import BranchSerializer, BranchListSerializer, BranchDetailSerializer
from .permissions import IsBranchOwner, IsAgencyAdminOrStaff
from vehicles.models import Vehicle
from vehicles.serializers import VehicleListSerializer


class BranchViewSet(ModelViewSet):
    lookup_field = 'slug'
    queryset = Branch.objects.all()

    def get_permissions(self):
        """
        This instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes =  [permissions.IsAuthenticated, IsBranchOwner]

        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsAgencyAdminOrStaff]
        
        # allow all other actions
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return BranchListSerializer
        elif self.action == 'retrieve':
            return BranchDetailSerializer
        return BranchSerializer  # For create/update

    # though permissions are good, but we need another safety net if permissions fail
    def get_queryset(self):
        user = self.request.user
        qs = Branch.objects.filter(is_active=True) # Public only sees active branches
        
        # If the user is staff, they should see their own branches (even inactive ones)
        if user.is_authenticated and (user.is_agency_admin() or user.is_agency_staff()):
            return Branch.objects.filter(agency=user.agency)
            
        return qs

    
    # extra security layer preventing non-agency-admins from creating branches for other agencies
    def perform_create(self, serializer):
        """
        Force the 'agency' field to be the logged-in user's agency.
        """
        serializer.save(agency=self.request.user.agency)

    # custom action for users to filter available / inventory cars at specific location

    @action(detail=True, methods=['get'], url_path='inventory')
    def get_inventory(self, request, slug=None):
        """
        Custom endpoint: GET /api/branches/{slug}/inventory/
        Returns all available vehicles currently parked at this branch.
        """

        branch = self.get_object()
        # Find vehicles linked to this branch that are marked as 'AVAILABLE'
        vehicles = Vehicle.objects.filter(current_location=branch, status='AVAILABLE')

        serializer = VehicleListSerializer(vehicles, many=True)
        return Response(serializer.data)