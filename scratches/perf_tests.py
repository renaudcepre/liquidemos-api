# noinspection PyUnresolvedReferences
import functools
from uuid import uuid4

import django_init
from scratches.utils import query_info

django_init.init()

from apps.projects.models import Tag, Delegation
from apps.users.models import User


def _make_user(**kwargs):
    kwargs['password'] = 'test_password'
    if 'username' not in kwargs:
        kwargs['username'] = str(uuid4())
    return User.objects.get_or_create(**kwargs)[0]


@query_info()
def create(number=1000):
    a = User.objects.get_or_create(username='root')[0]
    tag = Tag.objects.get_or_create(name='ISOLATED')[0]
    delegations = []

    for i in range(number):
        b = _make_user(username=str(i))
        delegations.append(Delegation(delegator=b,
                                      delegate=a,
                                      tag=tag))
        a = b
    Delegation.objects.bulk_create(delegations)


@query_info()
def create_cyclic():
    a = User.objects.get_or_create(username='a')[0]
    b = User.objects.get_or_create(username='b')[0]
    c = User.objects.get_or_create(username='c')[0]
    tag = Tag.objects.get_or_create(name='CYCLIC')[0]
    delegations = [
        Delegation(delegate=a, delegator=b, tag=tag),
        Delegation(delegate=b, delegator=c, tag=tag),
        Delegation(delegate=c, delegator=a, tag=tag)
    ]
    Delegation.objects.bulk_create(delegations)


def run():
    @query_info(show_sql=False)
    def iterative(user, tag):
        iterative = user.delegation_chain(tag, direction='out')
        # print(len(iterative))
        print(iterative)

    user = User.objects.get(username='a')
    tag = Tag.objects.get(name='CYCLIC')

    import statistics
    import timeit
    # iterative(user, tag)
    mean = statistics.mean(
        timeit.repeat(setup='from apps.users.models import User, Tag',
                      stmt=functools.partial(iterative, user, tag),
                      repeat=20,
                      number=1))
    print(f"Mean time: {mean:.4f}s")
    # print(statistics.mean(
    #     timeit.repeat(setup='from apps.users.models import User, Tag',
    #                   stmt=functools.partial(recursive, user, tag),
    #                   repeat=2,
    #                   number=1)))


if __name__ == '__main__':
    # create()
    # create_cyclic()
    run()
