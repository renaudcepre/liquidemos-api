import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from tests.tests_users.factories import UserFactory


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def registered_user():
    def _make():
        user = UserFactory(password="test")
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=True)
        return user

    return _make


@pytest.fixture
def logged_user_and_client(registered_user, api_client):
    def _make():
        user = registered_user()
        data = {"username": user.username,
                "password": 'test',
                }
        api_client.post(f"/api/auth/login/", data=data)
        return user, api_client

    return _make