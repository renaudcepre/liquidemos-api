import pytest

from apps.projects.models import Theme
from test_projects.factories import ProjectFactory


@pytest.fixture()
def create_project(db, registered_user):
    def _make(number=1, **data):
        projects = []
        for i in range(number):
            if 'created_by' not in data:
                data["created_by"] = registered_user()
            if 'theme' not in data:
                data["theme"], _ = Theme.objects.get_or_create(name='THEME')
            projects.append(ProjectFactory(**data))
        return projects[0] if number == 1 else projects

    return _make
