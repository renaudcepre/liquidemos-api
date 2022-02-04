from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet

from apps.projects.models import Delegation, Tag


class User(AbstractUser):

    def delegation_chain(self, tag, direction='in') -> QuerySet:
        assert direction in ('in', 'out')

        visited = []
        if direction == 'in':
            stack = list(self.incoming_delegations.filter(tag=tag))
        else:
            stack = list(self.outgoing_delegations.filter(tag=tag))

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.append(node)
                if direction == 'in':
                    qs = node.delegator.incoming_delegations.filter(tag=tag)
                else:
                    qs = node.delegate.outgoing_delegations.filter(tag=tag)
                stack.extend(list(qs))

        return Delegation.objects.filter(pk__in=[d.pk for d in visited])


class VoteWeight(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
