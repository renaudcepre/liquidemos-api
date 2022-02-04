from __future__ import annotations

import logging
import uuid

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.utils.text import slugify

from apps.projects.models import Project, AlternativeGroup, Vote, Tag, Delegation

logger = logging.getLogger(__name__)


@pytest.fixture
def create_user(db, django_user_model):
    """Return a closure that create a user with random values and default password."""

    def _make_user(**kwargs):
        kwargs['password'] = 'test_password'
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return _make_user


@pytest.fixture
def create_project(db, create_user):
    """Return a closure that create a project with random values."""

    def _make_project(**kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = str(uuid.uuid4())
        if 'created_by' not in kwargs:
            kwargs['created_by'] = create_user()
        return Project.objects.create(**kwargs)

    return _make_project


@pytest.fixture(scope='session')
def project_tree(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'test_projects.json')


class TestProject:
    def test_project_model(self, create_project):
        p = create_project(name='test project')
        p.save()
        assert p.path == '0'
        assert p.node_id == 0
        assert p.depth == 0
        assert p.name == 'test project'
        assert p.slug == slugify('test project')
        assert p.parent is None
        assert p.parents().count() == 0
        assert p.childs().count() == 0

    @pytest.mark.django_db
    def test_tree_direct_childs(self, project_tree):
        # get the top of the tree
        root = Project.objects.get(depth=0)

        assert root.childs(1).count() == 3

        for idx, child in enumerate(root.childs(1).all()):
            assert child.parent == root
            assert child.parents().count() == 1
            assert child.node_id == idx
            assert child.path == f'0/{idx}'
            assert child.depth == 1

    @pytest.mark.django_db
    def test_tree_grand_childs(self, project_tree):
        childs = Project.objects.filter(depth=2)

        for idx, child in enumerate(childs):
            # assert child.parent == root
            assert child.parents().count() == 2
            assert child.node_id == idx
            assert child.path.startswith("0/")
            assert child.path.endswith(str(idx))
            assert child.depth == 2

    @pytest.mark.django_db
    def test_retrieve_parents(self, project_tree):
        child = Project.objects.last()
        assert child.parents().count() == child.depth == 3
        assert child.path.startswith(child.parent.path)

    @pytest.mark.django_db
    def test_concurency_group(self, project_tree):
        childs = Project.objects.filter(depth=1)
        concurency_group = AlternativeGroup.objects.create()
        for child in childs:
            child.alternative_group = concurency_group
            child.save()
            assert concurency_group.project_set.contains(child)

        assert concurency_group.project_set.count() == 3

    @pytest.mark.django_db
    def test_include_self(self, project_tree):
        root: Project = Project.objects.get(depth=0)

        assert not root.childs().contains(root)
        assert root.childs(include_self=True).contains(root)

        child: Project = root.childs().last()
        assert not child.parents().contains(child)
        assert child.parents(include_self=True).contains(child)


class TestVote:
    @pytest.mark.django_db
    def test_vote(self, admin_user, create_user, create_project):
        project = create_project(created_by=admin_user)
        user = create_user()
        vote = Vote.objects.create(project=project, user=user)

        assert project.upvotes == 1
        assert project.downvotes == 0

        vote.upvote = False
        vote.save()

        assert project.upvotes == 0
        assert project.downvotes == 1

        assert vote.user == user


class TestDelegation:
    def test_delegation(self, create_user):
        tag = Tag.objects.create(name='TAG')
        delegate = create_user(username="delegate")
        delegator = create_user(username="delegator")

        Delegation.objects.create(tag=tag,
                                  delegate=delegate,
                                  delegator=delegator)

        with pytest.raises(IntegrityError):
            # Check UniqueConstraints
            with transaction.atomic():
                Delegation.objects.create(tag=tag,
                                          delegate=delegate,
                                          delegator=delegator)
                Delegation.objects.create(tag=tag,
                                          delegate=create_user(),
                                          delegator=delegator)

        assert delegate.incoming_delegations.count() == 1
        assert delegate.outgoing_delegations.count() == 0
        assert delegator.incoming_delegations.count() == 0
        assert delegator.outgoing_delegations.count() == 1

        assert Delegation.objects.create(tag=tag,
                                         delegate=delegate,
                                         delegator=create_user())

        assert delegate.incoming_delegations.count() == 2

    def test_recurse(self, create_user):
        tag = Tag.objects.create(name='TAG')
        delegate = create_user()
        last_delegator = create_user()

        delegations = []
        for i in range(5):
            delegations.append(Delegation(tag=tag,
                                          delegate=delegate,
                                          delegator=create_user()))

        delegations.append(Delegation(tag=tag,
                                      delegate=delegate,
                                      delegator=last_delegator))

        Delegation.objects.bulk_create(delegations)

        # num 1     -> delegate         delegate -> ramdom_user
        # num 2     -> delegate
        # num 3     -> delegate
        # num 4     -> delegate
        # num 5     -> delegate
        # last_del  -> delegate

        assert Delegation.objects.count() == 6
        assert delegate.vote_weight(tag) == 6  # le delege a un poids de 6 votes
        assert last_delegator.vote_weight(tag) == 0  # le dernier a un poinds de zero

    #
    def test_simple_cycling(self, create_user):
        tag = Tag.objects.create(name='TAG')
        delegate = create_user(username="delegate")
        delegator = create_user(username="delegator")

        Delegation.objects.create(tag=tag,
                                  delegate=delegate,
                                  delegator=delegator)

        Delegation.objects.create(tag=tag,
                                  delegate=delegator,
                                  delegator=delegate)

        logger.info(logger.name)
        assert delegate.delegation_chain(tag=tag), \
            "must not raise recursion error"

    def test_cycling(self, create_user):
        tag = Tag.objects.create(name='TAG')
        a = create_user(username="A")
        b = create_user(username="b")
        c = create_user(username="c")

        # c -> a -> b -> c
        delegations = [Delegation(tag=tag,
                                  delegate=a,
                                  delegator=c),
                       Delegation(tag=tag,
                                  delegate=b,
                                  delegator=a),
                       Delegation(tag=tag,
                                  delegate=c,
                                  delegator=b)]

        # let's give b some incoming delegations:
        for i in range(5):
            delegations.append(Delegation(tag=tag,
                                          delegator=create_user(),
                                          delegate=b))
        solo_user = create_user()
        delegations.append(Delegation(tag=tag,
                                      delegator=solo_user,
                                      delegate=b))

        Delegation.objects.bulk_create(delegations)

        a_result = a.delegation_chain(tag)
        assert a_result.count() == 9
        assert solo_user.vote_weight(tag) == 0

        assert list(a_result) \
               == list(c.delegation_chain(tag)) \
               == list(b.delegation_chain(tag))
