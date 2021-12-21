from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.projects.models import Project
from apps.users.models import User


class Command(BaseCommand):
    help = 'Create initial project data'

    def add_arguments(self, parser):
        parser.add_argument('depth', nargs='+', type=int)
        parser.add_argument('width', nargs='+', type=int)

    def handle(self, *args, **options):
        """Create a node tree with given depth and width"""
        # Clear previous data
        Project.objects.all().delete()

        depth = options['depth'][0]
        width = options['width'][0]

        user = User.objects.get_or_create(username='rcepre', is_superuser=True)[0]

        time = datetime.now()
        # Create the top node.
        first_node = Project.objects.create(parent=None, path='0', depth=0,
                                            created_by=user, name='0')
        line = [first_node]
        with transaction.atomic():
            for row in range(depth):
                print(f'depth: {row} .... ', end='')
                new_line = []
                for parent in line:
                    for i in range(width):
                        new_node = Project(
                            parent=parent,
                            created_by=user, name=f'd{row}i{i}')
                        new_node.save()

                        new_line.append(new_node)
                print(f"{len(new_line)} nodes.")
                line = new_line
        print(f"Created {Project.objects.count()} nodes "
              f"[{(datetime.now() - time).microseconds / 1000} ms]")
