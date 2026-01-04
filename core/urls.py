from django.urls import path
from .views import AgencyApplyView, AgencyMeView

urlpatterns = [
    path('agencies/apply/', AgencyApplyView.as_view(), name='agency-apply'),
    path('agencies/me/', AgencyMeView.as_view(), name='agency-me'),
]
