from rest_framework import status


def log_user(api_client, user, password='test'):
    data = {"username": user.username,
            "password": password,
            }

    login_response = api_client.post(f"/api/auth/login/", data=data)
    assert login_response.status_code == status.HTTP_200_OK
