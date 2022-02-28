from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


# noinspection PyMethodMayBeStatic
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
            if vote:
                vote.upvote = serializer.validated_data['upvote']
                vote.save()
                vote.update_vote_weight()
                serializer = VoteSerializer(vote)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                vote = serializer.save(project=project, user=user,
                                       weight=user.vote_weight(project))
                vote.update_vote_weight()
                return Response(serializer.validated_data,
                                status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        user = request.user
        vote = get_object_or_404(Vote, project=project, user=user)
        vote.delete()
        vote.update_vote_weight()
        return Response(status=status.HTTP_204_NO_CONTENT)
