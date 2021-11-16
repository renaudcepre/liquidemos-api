from django.db import models

from projects.models.tag import Tag
from workspace.models import Workspace


class Proposition(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)


class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    from_proposition = models.ForeignKey(Proposition, on_delete=models.PROTECT,
                                         null=True, blank=True,
                                         related_name='proposition')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"Project {self.name}"
