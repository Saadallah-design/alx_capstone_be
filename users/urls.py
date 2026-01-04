from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegistrationView, UserProfileView, CustomTokenObtainPairView, ChangePasswordView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'), # Using UserRegistrationView as per views.py
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('password/change/', ChangePasswordView.as_view(), name='change_password'),
]
