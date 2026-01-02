from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileDetailSerializer, CustomTokenObtainPairSerializer

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
