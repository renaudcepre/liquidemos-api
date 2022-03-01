import pytest
from rest_framework import status

from apps.projects.models import Delegation, Project
from tests.utils import log_user

pytestmark = pytest.mark.django_db


class TestVotes:
    endpoint = "/api/projects"

    def get_vote_url(self, project: Project):
        return f"{self.endpoint}/{project.slug}/vote"

    @pytest.mark.django_db
    def test_test(self, create_project, registered_user, api_client):
        user, user2, user3 = registered_user(number=3)
        project, project2 = create_project(number=2, created_by=user)
        Delegation.objects.bulk_create((
            Delegation(delegator=user2, delegate=user, theme=project.theme),
            Delegation(delegator=user3, delegate=user2, theme=project.theme)))

        log_user(api_client, user3)
        response = api_client.post(self.get_vote_url(project),
                                   data={'upvote': True})

        assert response.status_code == status.HTTP_200_OK
        assert project.vote_set.count() == 1

        assert user.vote_weight(project2) == 3
        assert user.vote_weight(project) == 2

        assert user2.vote_weight(project2) == 2
        assert user2.vote_weight(project) == 1

        assert user3.vote_weight(project2) == 1
        assert user3.vote_weight(project) == 1

