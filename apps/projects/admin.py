from django.contrib import admin

from apps.projects.models import Project, Tag

admin.site.register(Project)
admin.site.register(Tag)
