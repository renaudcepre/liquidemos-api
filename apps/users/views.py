from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.shortcuts import redirect

from liquidemos import settings


class PasswordResetConfirmView(PasswordResetConfirmView):
    """
    view for password reset in frontend , not backend
    """

    def get(self, *args, **kwargs):
        query = f"uid={kwargs['uidb64']}&token={kwargs['token']}"
        return redirect(f"{settings.FRONTEND_URL}/auth/new-password/?{query}")


class VerifyEmailView(VerifyEmailView):
    """
    view for verify email in frontend , not backend
    """

    def get(self, *args, **kwargs):
        query = f"key={kwargs['key']}"
        return redirect(f"{settings.FRONTEND_URL}/auth/verify-email/?{query}")

# class UserViewSet(viewsets.ModelViewSet):
#     """ A simple ViewSet for viewing and editing projects."""
#     queryset = User.objects.all()
#     serializer_class = BasicAccountSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_serializer_class(self):
#         if self.request.user.is_staff:
#             return FullAccountSerializer
#         return BasicAccountSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(date_joined=datetime.datetime.now())
