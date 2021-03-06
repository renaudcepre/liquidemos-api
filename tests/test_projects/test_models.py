from __future__ import annotations

import logging

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction

from apps.projects.models import *

logger = logging.getLogger(__name__)


@pytest.fixture()
def project_tree(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'test_projects.json')


@pytest.mark.django_db
class TestProject:
    def test_project_model(self, create_project):
        p = create_project(name='test project')
        p.save()
        assert p.path == '0', f"path {Project.objects.count()}"
        assert p.node_id == 0, "mode_id"
        assert p.depth == 0
        assert p.name == 'test project'
        assert p.slug == slugify('test project')
        assert p.parent is None
        assert p.parents().count() == 0
        assert p.childs().count() == 0

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

    def test_tree_grand_childs(self, project_tree):
        childs = Project.objects.filter(depth=2)

        for idx, child in enumerate(childs):
            # assert child.parent == root
            assert child.parents().count() == 2
            assert child.node_id == idx
            assert child.path.startswith("0/")
            assert child.path.endswith(str(idx))
            assert child.depth == 2

    def test_retrieve_parents(self, project_tree):
        child = Project.objects.last()
        assert child.parents().count() == child.depth == 3
        assert child.path.startswith(child.parent.path)

    def test_concurency_group(self, project_tree):
        childs = Project.objects.filter(depth=1)
        concurency_group = AlternativeGroup.objects.create()
        for child in childs:
            child.alternative_group = concurency_group
            child.save()
            assert concurency_group.project_set.contains(child)

        assert concurency_group.project_set.count() == 3

    def test_include_self(self, project_tree):
        root: Project = Project.objects.get(depth=0)

        assert not root.childs().contains(root)
        assert root.childs(include_self=True).contains(root)

        child: Project = root.childs().last()
        assert not child.parents().contains(child)
        assert child.parents(include_self=True).contains(child)


@pytest.mark.django_db
class TestVote:
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

    def test_votes_updates_when_user_vote(self, create_user, create_project):
        project = create_project()
        user0, user1, user2, user3 = create_user(number=4)
        Delegation.objects.bulk_create((
            Delegation(delegate=user3, delegator=user2, theme=project.theme),
            Delegation(delegate=user2, delegator=user1, theme=project.theme),
            Delegation(delegate=user1, delegator=user0, theme=project.theme),
        ))
        user3_vote = Vote(user=user3, project=project)
        user3_vote.save()

        assert user3_vote.weight == 4

        user2_vote = Vote(user=user2, project=project)
        user2_vote.save()
        user3_vote.refresh_from_db()

        assert user3_vote.weight == 1
        assert user2_vote.weight == 3

        user2_vote.delete()
        user3_vote.refresh_from_db()

        assert user3_vote.weight == 4

    def test_votes_updates_when_user_delegate(self, create_user,
                                              create_project):
        project = create_project()
        user0, user1, user2, user3 = create_user(number=4)
        Delegation.objects.bulk_create((
            Delegation(delegate=user3, delegator=user2, theme=project.theme),
            Delegation(delegate=user2, delegator=user1, theme=project.theme),
        ))
        user3_vote = Vote(user=user3, project=project)
        user3_vote.save()

        assert user3_vote.weight == 3

        delegation = Delegation.objects.create(delegate=user1, delegator=user0,
                                               theme=project.theme)
        user3_vote.refresh_from_db()
        assert user3_vote.weight == 4

        delegation.delete()
        user3_vote.refresh_from_db()
        assert user3_vote.weight == 3


@pytest.mark.django_db
class TestDelegation:
    def test_delegation(self, create_user):
        theme = Theme.objects.create(name='THEME')
        Project.objects.create(name='TEST',
                               theme=theme,
                               created_by=create_user())
        delegate = create_user(username="delegate")
        delegator = create_user(username="delegator")

        Delegation.objects.create(theme=theme,
                                  delegate=delegate,
                                  delegator=delegator)

        with pytest.raises(IntegrityError):
            # Check UniqueConstraints
            with transaction.atomic():
                Delegation.objects.create(theme=theme,
                                          delegate=delegate,
                                          delegator=delegator)
                Delegation.objects.create(theme=theme,
                                          delegate=create_user(),
                                          delegator=delegator)

        assert delegate.incoming_delegations.count() == 1
        assert delegate.outgoing_delegations.count() == 0
        assert delegator.incoming_delegations.count() == 0
        assert delegator.outgoing_delegations.count() == 1

        assert Delegation.objects.create(theme=theme,
                                         delegate=delegate,
                                         delegator=create_user())

        assert delegate.incoming_delegations.count() == 2

    def test_recurse(self, create_user):
        theme = Theme.objects.create(name='THEME')
        other_theme = Theme.objects.create(name='OTHER_THEME')
        project = Project.objects.create(name='TEST',
                                         theme=theme,
                                         created_by=create_user())
        delegate = create_user(username='delegate')
        last_delegator = create_user(username='last_delegator')

        delegations = []
        for i in range(5):
            delegations.append(Delegation(theme=theme,
                                          delegate=delegate,
                                          delegator=create_user(
                                              username=str(i))))
            # Create delegation with other theme for ensure that the filtering
            # work
            delegations.append(Delegation(theme=other_theme,
                                          delegate=delegate,
                                          delegator=create_user()))

        delegations.append(Delegation(theme=theme,
                                      delegate=delegate,
                                      delegator=last_delegator))

        Delegation.objects.bulk_create(delegations)

        # For Theme THEME
        # num 1     -> delegate
        # num 2     -> delegate
        # num 3     -> delegate
        # num 4     -> delegate
        # num 5     -> delegate
        # last_del  -> delegate

        assert delegate.delegation_chain(project).count() == 6
        assert last_delegator.delegation_chain(project).count() == 0
        assert delegate.delegation_chain(project, 'out').count() == 0
        assert last_delegator.delegation_chain(project, 'out').count() == 1

    def test_simple_cycling(self, create_user):
        theme = Theme.objects.create(name='THEME')
        project = Project.objects.create(name='TEST',
                                         theme=theme,
                                         created_by=create_user())
        delegate = create_user(username="delegate")
        delegator = create_user(username="delegator")

        Delegation.objects.create(theme=theme,
                                  delegate=delegate,
                                  delegator=delegator)

        Delegation.objects.create(theme=theme,
                                  delegate=delegator,
                                  delegator=delegate)

        assert delegate.delegation_chain(target=project).count() == 1

    def test_cycling(self, create_user):
        theme = Theme.objects.create(name='THEME')
        project = Project.objects.create(name='TEST',
                                         theme=theme,
                                         created_by=create_user())
        a = create_user(username="A")
        b = create_user(username="b")
        c = create_user(username="c")

        # c -> a -> b -> c
        delegations = [Delegation(theme=theme,
                                  delegate=a,
                                  delegator=c),
                       Delegation(theme=theme,
                                  delegate=b,
                                  delegator=a),
                       Delegation(theme=theme,
                                  delegate=c,
                                  delegator=b)]

        # let's give b some incoming delegations:
        for i in range(5):
            delegations.append(Delegation(theme=theme,
                                          delegator=create_user(),
                                          delegate=b))
        solo_user = create_user()
        delegations.append(Delegation(theme=theme,
                                      delegator=solo_user,
                                      delegate=b))

        Delegation.objects.bulk_create(delegations)

        a_result = a.delegation_chain(target=project)
        assert a_result.count() == 8
        assert solo_user.vote_weight(project=project) == 1

        assert (a.vote_weight(project=project) ==
                b.vote_weight(project=project) ==
                c.vote_weight(project=project))

    def test_cycling_cutted_by_vote(self, create_user):
        theme = Theme.objects.create(name='THEME')
        project = Project.objects.create(name='TEST',
                                         theme=theme,
                                         created_by=create_user())
        a = create_user(username="A")
        b = create_user(username="b")
        c = create_user(username="c")

        # c -> a -> b -> c
        # 4 -> 2 -> 3 -> 4
        delegations = [Delegation(theme=theme,
                                  delegate=a,
                                  delegator=c),
                       Delegation(theme=theme,
                                  delegate=b,
                                  delegator=a),
                       Delegation(theme=theme,
                                  delegate=c,
                                  delegator=b)]

        Delegation.objects.bulk_create(delegations)

        # b vote for the project.
        Vote.objects.create(project=project, user=b)

        assert a.vote_weight(project=project) == 2
        assert b.vote_weight(project=project) == 3
        assert c.vote_weight(project=project) == 1

    def test_delegation_chain(self, create_user, create_project):
        project = create_project()
        user0, user1, user2, user3 = create_user(number=4)
        Delegation.objects.bulk_create((
            Delegation(delegate=user3, delegator=user2, theme=project.theme),
            Delegation(delegate=user2, delegator=user1, theme=project.theme),
        ))

        assert (list(user3.delegation_chain(project)) ==
                list(user3.delegation_chain(project.theme))), \
            "pass a theme or a project as target parameter should give " \
            "the same result"
        assert (list(user3.delegation_chain(project, 'out')) ==
                list(user3.delegation_chain(project.theme, 'out'))), \
            "pass a theme or a project as target parameter should give " \
            "the same result"

        Vote.objects.create(user=user2, project=project)
        # When a user vote for a project, he cut the delegation chain for this
        # project, but not for the theme. Since user2 has voted for the
        # project, user3 now have an empty delegation_chain
        assert user3.delegation_chain(project).count() == 0
        assert user3.delegation_chain(project.theme).count() == 2

    def test_delegation_chain_bad_param(self, create_user):
        user = create_user()
        with pytest.raises(AssertionError):
            user.delegation_chain(target=user)
