from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.users.views import UserViewSet

router = SimpleRouter()
router.register('users', UserViewSet, 'user')

urlpatterns = [
    path("", include(router.urls)),
    # Password Reset
    path('auth/password-reset/', PasswordResetView.as_view()),
    path('auth/password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Login / logout / password change / user
    path("auth/", include("dj_rest_auth.urls")),

    # Registration
    path('auth/register/', RegisterView.as_view()),

    # Account confirmation
    path('auth/account-confirm-email/<str:key>/', ConfirmEmailView.as_view(),
         name='account_confirm_email'),
    path('auth/account-confirm-email/', VerifyEmailView.as_view(),
         name='account_email_verification_sent'),
]
