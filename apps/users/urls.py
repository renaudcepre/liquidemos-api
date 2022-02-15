from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView

from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView

from django.urls import path, include

urlpatterns = [
    # Password Reset
    path('password-reset/', PasswordResetView.as_view()),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Login / logout / password change / user
    path("", include("dj_rest_auth.urls")),

    # Registration
    path('register/', RegisterView.as_view()),

    # Account confirmation
    path('account-confirm-email/<str:key>/', ConfirmEmailView.as_view(),
         name='account_confirm_email'),
    path('account-confirm-email/', VerifyEmailView.as_view(),
         name='account_email_verification_sent'),
]
