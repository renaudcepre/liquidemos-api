from django.apps import apps
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def vote_weight(self, tag):
        pass

    def delegation_chain(self, tag) -> QuerySet:
        the_list = list(Delegation.objects.select_related('delegator', 'delegate').filter(tag=tag))

        def _recurse(user) -> list:
            delegation_list = []
            delegations = [a for a in the_list if a.delegate == user]

            for d in delegations:
                delegation_list += _recurse(d.delegator)
                delegation_list.append(d)
            return delegation_list

        pk_list = [d.pk for d in _recurse(self)]
        return Delegation.objects.filter(pk__in=pk_list)
