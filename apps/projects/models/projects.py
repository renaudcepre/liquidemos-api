from django.db import models

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.projects.models.tag import Tag
from apps.users.models import User


class Alternative(DatedModelMixin, models.Model):
    """Alternative contains the real proposition, and can be 'forked' ad another alternative."""
    content = models.TextField()
    proposition = models.ForeignKey('Proposition', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alternative {self.id} for  {self.proposition.name}"


class Proposition(models.Model):
    """A proposition is defined by these alternatives."""
    name = models.CharField(max_length=64)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Proposition {self.name} ({self.alternative_set.count()} alternatives)"


class Project(DatedModelMixin, models.Model):
    """A project contains a number of propositions."""
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    from_proposition = models.ForeignKey(Proposition, on_delete=models.PROTECT,
                                         null=True, blank=True,
                                         related_name='proposition')
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"Project {self.name}"
