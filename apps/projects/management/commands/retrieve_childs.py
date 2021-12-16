import random
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.projects.models import Project


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'



    def handle(self, *args, **options):
        base: Project = Project.objects.first()
        t1 = datetime.now()
        childs = base.childs(5)
        print(f"Retrieved {childs.count()} nodes [{(datetime.now() - t1).microseconds / 1000} ms]  on {Project.objects.count()} nodes.")
