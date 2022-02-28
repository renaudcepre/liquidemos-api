from typing import Optional

from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.commons.utils.mptree.models import MaterializedPathNodeModel


class Theme(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Delegation(DatedModelMixin, models.Model):
    theme = models.ForeignKey(Theme,
                              on_delete=models.CASCADE)
    delegate = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                 related_name='incoming_delegations')
    delegator = models.ForeignKey("users.User", on_delete=models.CASCADE,
                                  related_name='outgoing_delegations')

    class Meta:
        constraints = [
            # A user can delegate his vote for one tag to one user.
            models.UniqueConstraint(fields=['delegator', 'theme'],
                                    name='unique delegation')]

    def __str__(self):
        return f"{self.delegator} -> {self.delegate} " \
               f"for {self.theme.name}"


class Vote(DatedModelMixin, models.Model):
    upvote = models.BooleanField(null=False, blank=False, default=True)
    weight = models.PositiveIntegerField(default=0, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # A user can only vote once for a project.
            models.UniqueConstraint(fields=['user', 'project'],
                                    name='unique vote')]

    def save(self, *args, **kwargs):
        self.weight = self.user.vote_weight(self.project)
        super().save(*args, **kwargs)

    def update_vote_weight(self):
        delegations = self.user.delegation_chain(self.project, direction='out')
        delegates = [d.delegate for d in delegations]
        votes = Vote.objects.filter(user__in=delegates, project=self.project)
        for vote in votes:
            vote.weight = vote.user.vote_weight(vote.project)
        Vote.objects.bulk_update(votes, fields=('weight',))

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
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(editable=False)
    tags = models.ManyToManyField(Tag, blank=True)

    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)

    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)

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
