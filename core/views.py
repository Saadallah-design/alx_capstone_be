from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Agency
from .serializers import AgencyApplicationSerializer

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
