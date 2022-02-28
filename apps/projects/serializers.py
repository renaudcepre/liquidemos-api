from rest_framework import serializers

from apps.projects.models import Project, Theme, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("upvote", "weight")
        read_only_fields = ('project', "weight")
        extra_kwargs = {'upvote': {'required': True}}


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    def get_score(self, instance):
        total = 0
        for vote in instance.vote_set.all():
            total += vote.weight if vote.upvote else -vote.weight

        return total

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "theme",
            "created_by",
            'score',
        ]

        read_only_fields = ("created_by", "slug")
