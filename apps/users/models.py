from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

from apps.projects.models import Delegation, Tag


class User(AbstractUser):

    def delegation_chain(self, tag, direction='in') -> QuerySet:
        assert direction in ('in', 'out')

        qs = Delegation.objects.filter(tag=tag)

        if direction == 'in':
            qs = qs.values_list('delegator__pk', 'delegate__pk', 'pk')
        else:
            qs = qs.values_list('delegate__pk', 'delegator__pk', 'pk')

        visited = []
        as_list = list(qs)
        stack = list(filter(lambda x: x[1] == self.pk, as_list))

        while stack:
            node = stack.pop()
            visited.append(node[2])
            as_list.remove(node)
            stack.extend(filter(lambda x: x[1] == node[0], as_list))

        return Delegation.objects.filter(pk__in=visited)
