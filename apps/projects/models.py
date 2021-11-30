from django.db import models
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Alternative(DatedModelMixin, models.Model):
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

    slug = models.SlugField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    from_proposition = models.ForeignKey(Proposition, on_delete=models.PROTECT,
                                         null=True, blank=True,
                                         related_name='proposition')
    tags = models.ManyToManyField(Tag, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Project {self.name}"