from apps.commons.management.base import CreateDataBaseCommand

from apps.users.factories import UserFactory


class Command(CreateDataBaseCommand):
    help = 'Create few users'

    def handle(self, *args, **options):
        super().handle(*args, **options)
        self.stdout.write(f'Creating {self.number} users ...')
        UserFactory.create_batch(size=self.number)
