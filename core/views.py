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
            "message": "Application submitted successfully. Our team will review your details within 24-48 hours.",
            "data": response.data
        }, status=status.HTTP_201_CREATED)
