import logging
from typing import List

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import QuerySet
from django.db.models.functions import Length
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.users.models import User

logger = logging.getLogger(__name__)

models.CharField.register_lookup(Length, 'length')


def next_id(row: QuerySet):
    node_ids: List[int] = [n.node_id for n in row]
    assert node_ids == sorted(node_ids)

    if len(node_ids) == 0 or node_ids[0] != 0:
        return 0

    for i, n in enumerate(node_ids):
        if i > 0 and node_ids[i - 1] != node_ids[i] - 1:
            return n - 1
    return row.count()


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
            if self.parent is None:
                tops = Project.objects.filter(path__length=1)
                free = next_id(tops)
                self.path = hex(free)[2:]
                self.depth = 0
            else:
                self.depth = self.parent.depth + 1
                row = Project.objects.filter(depth=self.depth)
                free = next_id(row)
                self.path = self.parent.path + '/' + hex(free)[2:]

        super().save(*args, **kwargs)

    @property
    def node_id(self) -> int:
        """Parse and retrun the name of the node in the path """
        return int(self.path.rpartition('/')[2], 16)

    def parents(self, depth: int = 0) -> QuerySet:
        """Query all childs of the node in the given depth, and return them as a queryset"""
        path = self.path
        # Create a list of all the parents paths
        paths = [path[0:x] for x in [i for i, c in enumerate(path) if c == '/']][-depth:]

        qs = Project.objects.filter(path__in=paths)
        return qs

    def childs(self, depth: int = 0) -> QuerySet:
        """Query all parents of the node in the given depth, and return them as a queryset"""
        qs = Project.objects.filter(path__startswith=self.path)
        if depth > 0:
            qs = qs.filter(depth__lt=self.depth + depth + 1)
        return qs.exclude(pk=self.pk)

    def __str__(self):
        return self.path

    class Meta:
        # allow to have a list as '0, 1, 0/1, 0/2' instead of '0, 0/1, 0/2, 1'
        ordering = ['path__length', 'path']
