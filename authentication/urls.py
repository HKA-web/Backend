from rest_framework import routers
from .views.user import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
