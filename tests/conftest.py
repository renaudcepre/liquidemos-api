import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def registered_user():
    def _make():
        user = get_user_model()(username='test_user')
        user.set_password('test')
        user.email = 'test@test.test'
        user.is_superuser = False
        user.is_staff = False
        user.is_active = True
        user.save()
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=True)
        return user

    return _make
