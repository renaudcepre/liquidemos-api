from django.contrib import admin

from apps.projects.models import Project, Tag, ConcurrencyGroup

admin.site.register(Project)
admin.site.register(Tag)
admin.site.register(ConcurrencyGroup)
