import logging
import random
from typing import List

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Value
from django.db.models.functions import Length, Replace
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.users.models import User

logger = logging.getLogger(__name__)

models.CharField.register_lookup(Length, 'length')


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Project(DatedModelMixin, models.Model):
    # MATERIALIZED PATH TREE
    path = models.CharField(max_length=1024, db_index=True, unique=True, editable=False)
    depth = models.IntegerField(editable=False, null=False)
    parent = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='fk_childs')

    # PROJECT
    name = models.CharField(max_length=64,
                            validators=[RegexValidator(r'^[a-zA-Z-1-9-_ ]*$')])
    description = models.TextField(blank=True)
    slug = models.SlugField(editable=False)
    tags = models.ManyToManyField(Tag, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Ne doivent pas etre ni parents, ni alternatives
    depends_on = models.ManyToManyField("Project",
                                        related_name='dependencies',
                                        blank=True)
    # Les alternatives doivent avoir le meme parent, et ne pas etre dependants
    # les unes des autres
    alternatives = models.ManyToManyField("Project", blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if not self.pk:
            logger.info("New Node created, create path for it.")

            # if self.parent is None:
            #     tops = Project.objects.filter(path__length=1)
            #     self.path = hex(tops.count())[2:]
            #     self.depth = 0
            # else:
            #     self.depth = self.parent.depth + 1
            #     self.path = self.parent.path + '/' + hex(max(
            #         [c.row_index for c in Project.objects.filter(depth=self.depth)]))[2:]

        super().save(*args, **kwargs)

    @property
    def row_index(self) -> int:
        return int(self.path.rpartition('/')[2], 16)

    def parents(self, depth=0):
        paths = [self.path[0:x] for x in [i for i, c in enumerate(self.path) if c == '/']][-depth:]
        qs = Project.objects.filter(path__in=paths).order_by('-path__length')
        return qs

    # def childs(self, depth=0):
    #     qs = Project.objects.filter(depth__gt=self.depth, path__startswith=self.path)
    #     if depth > 0:
    #         qs = Project.objects.filter(depth__lt=self.depth + depth + 1)
    #     return qs.exclude(pk=self.pk)

    def childs(self, depth=0):
        qs = Project.objects.filter(path__startswith=self.path)
        if depth > 0:
            qs = qs.filter(depth__lt=self.depth + depth + 1)
            # other tehcniques, slower but interresting:
            # qs = qs.annotate(dd=Length('path') - Length(Replace('path', Value('/')))).filter(dd__lt=depth + 1)
            # or
            # reg = '^' + self.path + r'(/[A-Z0-9]+){,' + str(depth) + '}$'
            # qs = qs.filter(path__regex=reg)

        return qs.exclude(pk=self.pk)

    def __str__(self):
        return self.path
        # if not self.parent:
        #     return f"{self.path}"
        # if len(self.parents()) == 1:
        #     return f"{self.parent.path}/{self.path}"
        # return f"{self.parents()[-1].path}/.../{self.path}"

# @receiver(m2m_changed, sender=Project.depends_on.through)
# def validate_depends(sender, action, instance: Project, **kwargs):
#     """Chek that the projects added as dependencies are not parents or alternatives."""
#     if action == 'post_add':
#         parent_list = instance.parents
#         for rel in instance.depends_on.all():
#             if rel == instance:
#                 raise ValidationError(f"Can depends on itself")
#             if rel in parent_list:
#                 raise ValidationError(f'This project already depends on "{rel}" by inheritance.')
#             if rel in instance.alternatives.all():
#                 raise ValidationError(
#                     f'{rel} cannot be added as dependencie, because its an alternative to that project')
#
#
# @receiver(m2m_changed, sender=Project.alternatives.through)
# def validate_alternatives(sender, action, instance: Project, **kwargs):
#     """"""
#     if action == 'post_add':
#         for alternative in instance.alternatives.all():
#             if alternative == instance:
#                 raise ValidationError(f"Cannot be an alternative to itself")
#             if alternative.parent != instance.parent:
#                 raise ValidationError(f'Alternatives have to share the same parent')
#             if alternative in instance.alternatives.all() or instance in alternative.alternatives.all():
#                 raise ValidationError(
#                     f'{alternative} cannot be added as alternative, because its a dependencie to that project')
