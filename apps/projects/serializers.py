from rest_framework import serializers

from apps.projects.models import Project, Theme, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("upvote",)
        read_only_fields = ('project', 'user')


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "theme",
            "created_by",
            'upvotes',
            'downvotes',
        ]

        read_only_fields = ("created_by", "slug")
