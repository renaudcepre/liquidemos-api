from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet, Q

from apps.projects.models import Delegation, Project, Theme
from liquidemos.settings import logger


class User(AbstractUser):

    def vote_weight(self, project: Project):
        return self.delegation_chain(target=project).count() + 1

    def delegation_chain(self, target: Project | Theme,
                         direction='in') -> QuerySet:
        logger.info(f'Pass into delegation chain for {target}')
        """
        Query the set of delegations in the database for the project topic
        passed as an argument, and traverses the delegation tree to return a
        set of queries containing all the delegations given to the user.
        The 'direction' parameter specifies whether we want all delegations
        given by users or those given to the user.

        """
        assert direction in ('in', 'out')
        assert isinstance(target, (Project, Theme))
        project = target if isinstance(target, Project) else None
        theme = target if isinstance(target, Theme) else project.theme

        qs = Delegation.objects.filter(theme=theme)
        if project:
            voters = [p.user for p in project.vote_set.exclude(user=self)]
            qs = qs.filter(~Q(delegator__in=voters))

        if direction == 'in':
            qs = qs.values_list('delegator__pk', 'delegate__pk', 'pk').exclude(
                delegator=self)
        else:
            qs = qs.values_list('delegate__pk', 'delegator__pk', 'pk').exclude(
                delegate=self)

        as_list = list(qs)
        visited = []
        stack = list(filter(lambda x: x[1] == self.pk, as_list))

        while stack:
            node = stack.pop()
            visited.append(node[2])
            as_list.remove(node)
            stack.extend(list(filter(lambda x: x[1] == node[0], as_list)))

        return Delegation.objects.filter(pk__in=visited)
