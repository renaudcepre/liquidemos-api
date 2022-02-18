from django.db.models import Sum
from rest_framework import serializers

from apps.projects.models import Project, Theme, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("project", "user", "upvote", "weight")
        read_only_fields = ('project', 'user', "weight")
        extra_kwargs = {'upvote': {'required': True}}


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()

    def get_votes(self, instance):
        return instance.vote_set.aggregate(Sum('weight'))['weight__sum']

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "theme",
            "created_by",
            'votes',
        ]

        read_only_fields = ("created_by", "slug")
