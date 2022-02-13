from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import Project, Theme
from apps.projects.serializers import ProjectSerializer, ThemeSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

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
