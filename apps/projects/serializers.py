from rest_framework import serializers

from apps.projects.models import Project, Theme


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "theme",
            "created_by",
        ]

        read_only_fields = ("created_by", "slug")
