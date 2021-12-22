import pytest
from django.db.models import QuerySet

from apps.projects.models import Project, ConcurrencyGroup
from apps.users.models import User


@pytest.fixture
def superuser() -> User:
    return User.objects.create_superuser(username='admin',
                                         email='admin@admin.com',
                                         password='password')


@pytest.fixture
def project_tree(superuser) -> QuerySet:
    root = Project(name='This is a test', parent=None,
                   created_by=superuser)
    root.save()

    for i in range(3):
        Project(name=f"child n{i}", parent=root,
                created_by=superuser).save()

    Project(name='child', parent=root.childs().first(),
            created_by=superuser).save()
    assert Project.objects.count() == 5
    return Project.objects.all()


@pytest.mark.django_db
def test_project_model(superuser):
    p = Project(name='This is a test', parent=None, created_by=superuser)
    p.save()
    assert p.path == '0'
    assert p.node_id == 0
    assert p.depth == 0
    assert p.name == 'This is a test'
    assert p.slug == 'this-is-a-test'
    assert p.parent is None
    assert p.parents().count() == 0
    assert p.childs().count() == 0


@pytest.mark.django_db
def test_tree_direct_childs(project_tree):
    root = project_tree.get(depth=0)

    assert root.childs(1).count() == 3

    for idx, child in enumerate(root.childs(1).all()):
        assert child.parent == root
        assert child.parents().count() == 1
        assert child.parents().first() == root
        assert child.node_id == idx
        assert child.path == f'0/{idx}'
        assert child.depth == 1


@pytest.mark.django_db
def test_tree_childs_depth(project_tree):
    root = project_tree.get(depth=0)

    child = root.childs().last()
    assert child.path == '0/0/0'
    assert child.node_id == 0
    assert child.depth == 2
    assert child.parents().count() == 2
    assert child.parents(1).first() == child.parent
    assert root.childs().count() == 4
    assert root.childs(1).count() == 3


@pytest.mark.django_db
def test_concurency_group(project_tree):
    childs = project_tree.filter(depth=1)
    concurency_group = ConcurrencyGroup.objects.create()
    for child in childs:
        child.concurrency_group = concurency_group
        child.save()

    assert concurency_group.project_set.count() == 3


@pytest.mark.django_db
def test_indlude_self(project_tree):
    root: Project = project_tree.get(depth=0)

    assert not root.childs().contains(root)
    assert root.childs(include_self=True).contains(root)

    child: Project = root.childs().last()
    assert not child.parents().contains(child)
    assert child.parents(include_self=True).contains(child)
