from django.contrib import admin

from projects.models.projects import Project
from projects.models.tag import Tag


admin.site.register(Project)
admin.site.register(Tag)
