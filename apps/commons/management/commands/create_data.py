from django.core.management.base import BaseCommand

from django.core import management


class Command(BaseCommand):

    help = 'Create test data'

    def handle(self, *args, **options):
        management.call_command('create_users', number=5)