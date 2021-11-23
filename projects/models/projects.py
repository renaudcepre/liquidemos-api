from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from projects.models.tag import Tag
from workspace.models import Workspace


class Alternative(models.Model):
    """Alternative contains the real proposition, and can be 'forked' ad another alternative."""
    content = models.TextField()
    proposition = models.ForeignKey('Proposition', on_delete=models.CASCADE)
#     Todo: votes, comments ...

    def __str__(self):
        return f"Alternative {self.id} for  {self.proposition.name}"


class Proposition(models.Model):
    """A proposition is defined by these alternatives."""
    name = models.CharField(max_length=64)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    def __str__(self):
        return f"Proposition {self.name} ({self.alternative_set.count()} alternatives)"

class Project(models.Model):
    """A project contains a number of propositions."""
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    from_proposition = models.ForeignKey(Proposition, on_delete=models.PROTECT,
                                         null=True, blank=True,
                                         related_name='proposition')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"Project {self.name}"
