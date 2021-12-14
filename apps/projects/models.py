from typing import List

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Project(DatedModelMixin, models.Model):
    name = models.CharField(max_length=64,
                            validators=[RegexValidator(r'^[a-zA-Z-1-9-_ ]*$')])
    description = models.TextField(blank=True)

    slug = models.SlugField(editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    # Un parent est considere comme dependance de son enfant par default
    parent = models.ForeignKey("Project", on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='childs')
    # Ne doivent pas etre ni parents, ni alternatives
    depends_on = models.ManyToManyField("Project",
                                        related_name='dependencies',
                                        blank=True)
    # Les alternatives doivent avoir le meme parent, et ne pas etre dependants
    # les unes des autres
    alternatives = models.ManyToManyField("Project", blank=True)

    @property
    def parents(self) -> List:
        """@return the parents of the projects as list"""
        parents = []
        project = self
        while project.parent is not None:
            parents.append(project.parent)
            project = project.parent
        return parents

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if not self.parent:
            return f"{self.slug}"
        if len(self.parents) == 1:
            return f"{self.parent.slug}/{self.slug}"
        return f"{self.parents[-1].slug}/.../{self.slug}"


@receiver(m2m_changed, sender=Project.depends_on.through)
def validate_depends(sender, action, instance: Project, **kwargs):
    """Chek that the projects added as dependencies are not parents or alternatives."""
    if action == 'post_add':
        parent_list = instance.parents
        for rel in instance.depends_on.all():
            if rel == instance:
                raise ValidationError(f"Can depends on itself")
            if rel in parent_list:
                raise ValidationError(f'This project already depends on "{rel}" by inheritance.')
            if rel in instance.alternatives.all():
                raise ValidationError(
                    f'{rel} cannot be added as dependencie, because its an alternative to that project')


@receiver(m2m_changed, sender=Project.alternatives.through)
def validate_alternatives(sender, action, instance: Project, **kwargs):
    """"""
    if action == 'post_add':
        for alternative in instance.alternatives.all():
            if alternative == instance:
                raise ValidationError(f"Cannot be an alternative to itself")
            if alternative.parent != instance.parent:
                raise ValidationError(f'Alternatives have to share the same parent')
            if alternative in instance.alternatives.all() or instance in alternative.alternatives.all():
                raise ValidationError(
                    f'{alternative} cannot be added as alternative, because its a dependencie to that project')
