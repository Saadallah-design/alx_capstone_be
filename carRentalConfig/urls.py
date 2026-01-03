
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, # Optional: for verifying tokens
)

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/bookings/', include('rentals.urls')),
    path('api/branches/', include('branches.urls')),
]
