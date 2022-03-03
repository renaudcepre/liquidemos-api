from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.projects.models import Project, Theme, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("upvote", "weight")
        read_only_fields = ("weight",)
        extra_kwargs = {'upvote': {'required': True}}


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()
    theme = serializers.StringRelatedField()

    def get_score(self, instance):
        total = 0
        for vote in instance.vote_set.all():
            total += vote.weight if vote.upvote else -vote.weight

        return total

    def get_user_has_voted(self, instance):
        user = self.context.get('request').user
        try:
            vote = user.vote_set.get(project=instance)
            return 'up' if vote.upvote else 'down'
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "theme",
            "created_by",
            'score',
            'user_has_voted',
        ]

        read_only_fields = ("created_by", "slug")
