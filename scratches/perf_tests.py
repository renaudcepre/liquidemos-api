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


def run():
    # @query_info(show_sql=False)
    def iterative(user, tag):
        iterative = user.delegation_chain(tag, direction='in')
        print(len(iterative))

    user = User.objects.get(username='500')
    tag = Tag.objects.get(name='ISOLATED')

    # code(user, tag)
    import statistics
    import timeit
    print(statistics.mean(
        timeit.repeat(setup='from apps.users.models import User, Tag',
                      stmt=functools.partial(iterative, user, tag),
                      repeat=10,
                      number=1)))
    # print(statistics.mean(
    #     timeit.repeat(setup='from apps.users.models import User, Tag',
    #                   stmt=functools.partial(recursive, user, tag),
    #                   repeat=2,
    #                   number=1)))


if __name__ == '__main__':
    # create()
    run()
