from rest_framework import viewsets
from authentication.models.user import User
from authentication.serializers.user import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
