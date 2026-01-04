from django.urls import path
from .views import AgencyApplyView

urlpatterns = [
    path('agencies/apply/', AgencyApplyView.as_view(), name='agency-apply'),
]
