from django.db import models

from projects.models.tag import Tag
from workspace.models import Workspace


class Project(models.Model):
    name = models.CharField(max_length=64)
    parent = models.ForeignKey("Project", on_delete=models.PROTECT, null=True, blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"Project {self.name}"
