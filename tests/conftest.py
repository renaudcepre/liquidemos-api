import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from tests.tests_users.factories import UserFactory
from tests.utils import log_user


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _make(number=1, password='test', **kwargs):
        users = []
        for _ in range(number):
            users.append(UserFactory(password=password, **kwargs))
        return users[0] if number == 1 else users

    return _make


@pytest.fixture
def registered_user(create_user):
    def _make(password='test', number=1):
        users = []
        for _ in range(number):
            user = create_user(password=password)
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        primary=True,
                                        verified=True)
            users.append(user)

        return users[0] if number == 1 else users

    return _make


@pytest.fixture
def logged_user_and_client(registered_user, api_client):
    def _make(password='test'):
        user = registered_user(password=password)
        log_user(api_client, user, password=password)
        return user, api_client

    return _make
