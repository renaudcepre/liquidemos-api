from allauth.account.models import EmailAddress
from django.core.management import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = 'Create super user and confirmed allauth email.'

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username='admin')

        if created:
            user.set_password('admin')
            user.email = 'admin@site.com'
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        primary=True,
                                        verified=True)

            print(f'Administrator "{user}" created !')
        else:
            print(f'Administrator "{user}" already exist.')
