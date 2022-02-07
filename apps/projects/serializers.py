from rest_framework import serializers

from apps.projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id',
                  'name',
                  'description',
                  'tags',
                  'depends_on',
                  'alternative_group',
                  'created_by']

        read_only_fields = ('created_by', 'slug')
