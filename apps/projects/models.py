from typing import Optional

from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.commons.utils.mptree.models import MaterializedPathNodeModel
from apps.users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Vote(DatedModelMixin, models.Model):
    upvote = models.BooleanField(null=False, blank=False, default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)


class AlternativeGroup(models.Model):
    """Represents a set of projects that are alternatives to each other."""

    def __str__(self):
        return f"Group projects {', '.join([str(p.pk) for p in self.project_set.all()])}"


class Project(DatedModelMixin, MaterializedPathNodeModel):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    slug = models.SlugField(editable=False)
    tags = models.ManyToManyField(Tag, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    depends_on = models.ManyToManyField("Project",
                                        related_name='dependencies',
                                        blank=True)
    alternative_group = models.ForeignKey(AlternativeGroup,
                                          on_delete=models.SET_NULL,
                                          null=True, blank=True)

    @property
    def alternatives(self) -> Optional[QuerySet]:
        if self.alternative_group is not None:
            return self.alternative_group.project_set.exclude(pk=self.pk)
        return None

    @property
    def upvotes(self):
        """Used for list_display in admin panel"""
        return self.vote_set.filter(upvote=True).count()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})
