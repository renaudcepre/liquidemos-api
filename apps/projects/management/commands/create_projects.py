from apps.commons.management.base import CreateDataBaseCommand

from apps.projects.factories import ProjectFactory, PropositionFactory, AlternativeFactory


class Command(CreateDataBaseCommand):
    help = 'Create few projects'

    def handle(self, *args, **options):
        super().handle(*args, **options)
        self.stdout.write(f'Creating {self.number} projects ...')
        ProjectFactory.create_batch(size=self.number)
        self.stdout.write(f'With {self.number * 10} propositions ...')
        PropositionFactory.create_batch(size=self.number * 10)
        self.stdout.write(f'With {self.number * 20} alternatives ...')
        AlternativeFactory.create_batch(size=self.number * 20)
