from typing import Optional, List

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


class Delegation(DatedModelMixin, models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    delegate = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='incoming_delegations')
    delegator = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='outgoing_delegations')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['delegate', 'delegator', 'tag'],
                                    name='unique delegation')]

    @staticmethod
    def _recurse(user, tag, outgoing):
        del_list = []
        qs = user.incoming_delegations if outgoing else user.outgoing_delegations

        for delegation in qs.filter(tag=tag):
            del_list += Delegation.get_incomings(delegation.delegator, tag)
            del_list.append(delegation)
        return del_list

    @staticmethod
    def get_incomings(user: User, tag: Tag) -> QuerySet:
        """Return the list of all the delegation for the user for the specified
        tag recursively."""
        pk_list = [d.pk for d in Delegation._recurse(user, tag)]
        return Delegation.objects.filter(pk__in=pk_list)

    def __str__(self):
        return f"{self.delegator} -> {self.delegate} " \
               f"for {self.tag.name}"


class Vote(DatedModelMixin, models.Model):
    upvote = models.BooleanField(null=False, blank=False, default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} " \
               f"{'up' if self.upvote else ''}vote" \
               f" for {self.project}"


class AlternativeGroup(models.Model):
    """Represents a set of projects that are alternatives to each other."""

    def __str__(self):
        return f"Group projects " \
               f"{', '.join([str(p.pk) for p in self.project_set.all()])}"


class Project(DatedModelMixin, MaterializedPathNodeModel):
    """
    Represents a project, which can be voted and validated by the users.
    Each project can have child projects.
    The validation of a project depends on the validation of its children.
    """
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
        return self.vote_set.filter(upvote=True).count()

    @property
    def downvotes(self):
        return self.vote_set.filter(upvote=False).count()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})
