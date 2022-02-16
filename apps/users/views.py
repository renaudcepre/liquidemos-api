from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins

from apps.users.permissions import IsOwnOrReadOnly
from apps.users.serializers import UserSerializer


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnOrReadOnly]
    lookup_field = 'username'
