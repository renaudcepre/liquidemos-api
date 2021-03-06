import re

import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from rest_framework import status

from apps.users.models import User
from liquidemos import settings

pytestmark = pytest.mark.django_db


class TestRestAuthEndpoints:
    endpoint = '/api/auth'

    def get_verify_url(self, name: str):
        """
        Extract verification url form the email sended after registration
        """
        token_regex = rf"({self.endpoint}/{name}/[^\s]+)"
        regex_result = re.search(token_regex, mail.outbox[0].body)

        assert regex_result.groups()

        return regex_result.group(1)

    def test_register(self, api_client):
        """
        Test user regisration and account validation
        Does not respect the AAA principle because of the multiple verification
        of the account
        """

        url = f'{self.endpoint}/register/'

        data = {"username": "test_user",
                "email": "test@user.com",
                "password1": "Password1234..",
                "password2": "Password1234.."
                }

        response = api_client.post(
            url,
            data,
            format='json'
        )

        # User is created and the validation is sent to the user.
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {'detail': 'Verification e-mail sent.'}
        assert mail.outbox[0].to[0] == data['email']

        created_user = User.objects.get(username=data['username'])
        assert created_user

        # An EmailAdress object is created and the email is not verified
        allauth_user_email = EmailAddress.objects.get(email=data['email'])
        assert not allauth_user_email.verified

        # We send the GET request to verify the email address.
        verify_response = api_client.get(
            self.get_verify_url(name='account-confirm-email'))

        assert verify_response.status_code == status.HTTP_302_FOUND
        assert verify_response.url == settings.LOGIN_URL

        allauth_user_email.refresh_from_db()
        assert allauth_user_email.verified

    def test_login(self, registered_user, api_client):
        user = registered_user()

        data = {"username": user.username,
                "password": 'test',
                }

        login_response = api_client.post(f"{self.endpoint}/login/", data=data)
        user_response = api_client.get(f"{self.endpoint}/user/")

        assert login_response.status_code == status.HTTP_200_OK
        assert api_client.cookies[settings.JWT_AUTH_COOKIE]
        assert user_response.status_code == status.HTTP_200_OK
        assert user_response.data['username'] == user.username
        assert user_response.data['email'] == user.email

    def test_logout(self, logged_user_and_client):
        user, api_client = logged_user_and_client()
        response = api_client.post(f"{self.endpoint}/logout/")
        user_response = api_client.get(f"{self.endpoint}/user/")

        assert response.status_code == status.HTTP_200_OK
        assert user_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_current_user(self, logged_user_and_client):
        user, api_client = logged_user_and_client()
        user_response = api_client.get(f"{self.endpoint}/user/")

        assert user_response.status_code == status.HTTP_200_OK
        assert user_response.data['username'] == user.username
        assert user_response.data['email'] == user.email
        assert user_response.data['first_name'] == user.first_name
        assert user_response.data['last_name'] == user.last_name

    def test_password_reset(self, logged_user_and_client):
        user, api_client = logged_user_and_client(password='old_password')
        response = api_client.post(path=f"{self.endpoint}/password/reset/",
                                   data={"email": user.email})

        verify_url = self.get_verify_url(name='password-reset-confirm')
        uid, token, _ = verify_url.split('/')[-3:]
        data = {
            "new_password1": "new_password",
            "new_password2": "new_password",
            "uid": uid,
            "token": token
        }

        assert user.check_password('old_password')
        verify_response = api_client.post(
            path=verify_url,
            data=data)

        user.refresh_from_db()
        assert user.check_password('new_password')
        assert response.status_code == status.HTTP_200_OK
        assert verify_response.status_code == status.HTTP_200_OK
        assert verify_response.data == {
            'detail': 'Password has been reset with the new password.'}
