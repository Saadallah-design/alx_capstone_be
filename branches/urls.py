from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet


# using rest framework router to handle urls
# here the django will do the routing behind the scenes depending on the action 
# and depending on the http method
# and also since we r using @action, setting urls like this helps to automatically detect custom actions
router = DefaultRouter()
router.register(r'', BranchViewSet, basename='branch')

urlpatterns = router.urls
