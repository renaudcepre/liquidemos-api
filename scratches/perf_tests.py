# noinspection PyUnresolvedReferences
import functools
import statistics
import timeit
from uuid import uuid4

import django_init
from scratches.utils import query_info

django_init.init()

from apps.projects.models import Delegation, Project, Theme
from apps.users.models import User


def _make_user(**kwargs):
    kwargs['password'] = 'test_password'
    if 'username' not in kwargs:
        kwargs['username'] = str(uuid4())
    return User.objects.get_or_create(**kwargs)[0]


@query_info()
def create(number=1000):
    a = User.objects.get_or_create(username='root')[0]
    theme = Theme.objects.get_or_create(name='ISOLATED')[0]
    delegations = []

    for i in range(number):
        b = _make_user(username=str(i))
        delegations.append(Delegation(delegator=b,
                                      delegate=a,
                                      theme=theme))
        a = b
    Delegation.objects.bulk_create(delegations)


@query_info()
def create_cyclic():
    a, _ = User.objects.get_or_create(username='a')
    b, _ = User.objects.get_or_create(username='b')
    c, _ = User.objects.get_or_create(username='c')
    theme, _ = Theme.objects.get_or_create(name='theme')
    delegations = [
        Delegation(delegate=a, delegator=b, theme=theme),
        Delegation(delegate=b, delegator=c, theme=theme),
        Delegation(delegate=c, delegator=a, theme=theme)
    ]
    Delegation.objects.bulk_create(delegations)


def run():
    # @query_info(show_sql=False)
    def iterative(user, project):
        iterative = user.delegation_chain(project, direction='in')
        # print(len(iterative))
        # print(iterative)
        # print(user.vote_weight(project))

    user, _ = User.objects.get_or_create(username='root')
    theme, _ = Theme.objects.get_or_create(name='ISOLATED')
    project, _ = Project.objects.get_or_create(name='project', theme=theme,
                                               created_by=user)

    # iterative(user, project)
    mean = statistics.mean(
        timeit.repeat(setup='from apps.users.models import User',
                      stmt=functools.partial(iterative, user, project),
                      repeat=20,
                      number=10))
    print(f"Mean time: {mean:.4f}s")
    # print(statistics.mean(
    #     timeit.repeat(setup='from apps.users.models import User, Tag',
    #                   stmt=functools.partial(recursive, user, tag),
    #                   repeat=2,
    #                   number=1)))


if __name__ == '__main__':
    # pass
    # create()
    # create_cyclic()
    run()
