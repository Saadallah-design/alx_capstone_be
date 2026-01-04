from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileDetailSerializer, CustomTokenObtainPairSerializer, ChangePasswordSerializer
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

# UserRegistrationView
class UserRegistrationView(generics.CreateAPIView):
    # get all the users. Serializer is UserRegistrationSerializer
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    # allow any user to register
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        # this will pass the role='Customer' into the serializer's save() method
        serializer.save(role='CUSTOMER')

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            
            # Important: Password change typically invalidates existing tokens. 
            # Frontend should likely force a logout or refresh mechanism if needed.
            
            return Response({"status": "success", "message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
