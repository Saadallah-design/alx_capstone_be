from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgencyApplyView, AgencyMeView, AgencyStaffViewSet

router = DefaultRouter()
router.register(r'agencies/staff', AgencyStaffViewSet, basename='agency-staff')

urlpatterns = [
    path('agencies/apply/', AgencyApplyView.as_view(), name='agency-apply'),
    path('agencies/me/', AgencyMeView.as_view(), name='agency-me'),
    path('', include(router.urls)),
]
