from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import Project, Theme, Vote
from apps.projects.serializers import ProjectSerializer, ThemeSerializer, \
    VoteSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)


class ThemeViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing themes.
    """
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]


class VoteAPIView(generics.CreateAPIView):
    queryset = Vote.objects.all()

    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        project_slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=project_slug)
        upvote = serializer.validated_data['upvote']

        try:
            vote = project.vote_set.get(user=user)
        except ObjectDoesNotExist:
            vote = None

        if vote and vote.upvote == upvote:
            raise ValidationError(
                f"You have already given an {'up' if upvote else ''}vote on this project")
        elif vote:
            vote.upvote = upvote
            vote.save()
        else:
            serializer.save(project=project, user=user)
