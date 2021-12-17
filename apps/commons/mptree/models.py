from typing import List

from django.db import models
from django.db.models import QuerySet

from apps.commons.mptree.encoder import Encoder


class MaterializedPathNodeModel(models.Model):
    encoder = Encoder(charset=Encoder.CHARSET_44)
    assert encoder.charset.find('/') == -1
    path = models.CharField(max_length=1024, db_index=True, unique=True, editable=False)
    depth = models.IntegerField(editable=False, null=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='fk_childs')

    def save(self, *args, **kwargs):
        if not self.pk:
            # Create path
            if self.parent is None:
                tops = self.__class__.objects.filter(parent__isnull=True)
                free = self.next_id(tops)
                self.path = MaterializedPathNodeModel.encoder.encode(free)
                self.depth = 0
            else:
                self.depth = self.parent.depth + 1
                row = self.__class__.objects.filter(depth=self.depth)
                free = self.next_id(row)
                self.path = self.parent.path + '/' + MaterializedPathNodeModel.encoder.encode(free)
        super().save(*args, **kwargs)

    @property
    def node_id(self) -> int:
        """Parse and retrun the name of the node in the path """
        return MaterializedPathNodeModel.encoder.decode(self.path.rpartition('/')[2])

    def parents(self, depth: int = 0) -> QuerySet:
        """Query all childs of the node in the given depth, and return them as a queryset"""
        path = self.path
        # Create a list of all the parents paths
        paths = [path[0:x] for x in [i for i, c in enumerate(path) if c == '/']][-depth:]

        qs = self.__class__.objects.filter(path__in=paths)
        return qs

    def childs(self, depth: int = 0) -> QuerySet:
        """Query all parents of the node in the given depth, and return them as a queryset"""
        qs = self.__class__.objects.filter(path__startswith=self.path)
        if depth > 0:
            qs = qs.filter(depth__lt=self.depth + depth + 1)
        return qs.exclude(pk=self.pk)

    @staticmethod
    def next_id(row: QuerySet):
        """Looks for the first free identifier in the list"""

        node_ids: List[int] = sorted([n.node_id for n in row])

        if len(node_ids) == 0 or node_ids[0] != 0:
            return 0

        for i, node_id in enumerate(node_ids):
            if i > 0 and node_ids[i - 1] != node_ids[i] - 1:
                return node_id - 1
        return row.count()

    class Meta:
        abstract = True
        ordering = ['path__length', 'path']
