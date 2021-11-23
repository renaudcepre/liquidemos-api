from django.contrib import admin

from apps.projects.models.projects import Project, Proposition, Alternative
from apps.projects.models.tag import Tag


class PropositionInline(admin.TabularInline):
    model = Proposition


class ProjectAdmin(admin.ModelAdmin):
    inlines = [PropositionInline, ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Alternative)
admin.site.register(Tag)