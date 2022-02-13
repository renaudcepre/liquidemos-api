from rest_framework import serializers
from rest_framework.serializers import ALL_FIELDS

from apps.users.models import User


class BasicAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',
                   'last_login',
                   'user_permissions',
                   'groups',
                   'is_active',
                   )
        read_only_fields = ('date_joined',)


class FullAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ALL_FIELDS
        read_only_fields = ('date_joined',)
