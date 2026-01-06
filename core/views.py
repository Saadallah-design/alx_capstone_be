from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Agency, AgencyMember
from .serializers import AgencyApplicationSerializer, AgencyMemberSerializer

User = get_user_model()

class AgencyApplyView(generics.CreateAPIView):
    """
    Allow authenticated customers to apply for agency status.
    """
    serializer_class = AgencyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Override to provide a custom success message
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Application submitted successfully.",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

class AgencyMeView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for users to view and update their own agency profile.
    GET/PATCH /api/agencies/me/
    """
    serializer_class = AgencyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the agency profile linked to the user
        return get_object_or_404(Agency, user=self.request.user)

class AgencyStaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Agency Admins to manage their staff.
    """
    serializer_class = AgencyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Must be an agency admin to manage staff
        user = self.request.user
        if not (user.is_authenticated and user.is_agency_admin()):
            return AgencyMember.objects.none()
        
        agency = getattr(user, 'agency_profile', None)
        if not agency:
            return AgencyMember.objects.none()
            
        return AgencyMember.objects.filter(agency=agency).select_related('user')

    def create(self, request, *args, **kwargs):
        """
        Invite a staff member by email.
        """
        user = self.request.user
        if not user.is_agency_admin():
            return Response({"detail": "Only agency admins can invite staff."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        if not email:
            return Response({"email": "This field is required."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Find the user
        try:
            invitee = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email not found. They must register first."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        # 2. Check if already a member of any agency
        if AgencyMember.objects.filter(user=invitee).exists():
            return Response({"detail": "User is already a staff member of an agency."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(invitee, 'agency_profile'):
            return Response({"detail": "User is already an agency admin."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Create membership
        agency = user.agency_profile
        membership = AgencyMember.objects.create(user=invitee, agency=agency)
        
        # 4. Update invitee role
        if invitee.role != 'AGENCY_STAFF':
            invitee.role = 'AGENCY_STAFF'
            invitee.save()
            
        serializer = self.get_serializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Remove a staff member and reset their role.
        """
        instance = self.get_object()
        user_to_remove = instance.user
        
        # Perform deletion
        self.perform_destroy(instance)
        
        # Reset role if they are no longer in any agency (one-to-one protects this currently)
        user_to_remove.role = 'CUSTOMER'
        user_to_remove.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
