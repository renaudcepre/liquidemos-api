from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project, Theme
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


class VoteAPIView(APIView):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        user = request.user
        try:
            vote = project.vote_set.get(user=user)
            serializer = VoteSerializer(vote)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"details": "You don't have voted for this project"},
                status=status.HTTP_404_NOT_FOUND)

    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        user = request.user
        try:
            vote = project.vote_set.get(user=user)
        except ObjectDoesNotExist:
            vote = None

        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            upvote = serializer.validated_data['upvote']
            if vote:
                vote.upvote = upvote
                vote.weight = user.vote_weight(project)
                vote.save()
                serializer = VoteSerializer(vote)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer.save(project=project, user=user,
                                weight=user.vote_weight(project))
                serializer = VoteSerializer(vote)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    # user = self.request.user
    # project_slug = self.kwargs.get('slug')
    # project = get_object_or_404(Project, slug=project_slug)
    # upvote = serializer.validated_data['upvote']
    #
    # try:
    #     vote = project.vote_set.get(user=user)
    # except ObjectDoesNotExist:
    #     vote = None
    #
    # if vote and vote.upvote == upvote:
    #     raise ValidationError(
    #         f"You have already given an {'up' if upvote else ''}vote on this project")
    # elif vote:
    #     vote.upvote = upvote
    #     vote.save()
    # else:
    #     serializer.save(project=project, user=user)
