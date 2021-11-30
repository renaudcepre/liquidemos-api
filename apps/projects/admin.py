from django.contrib import admin

from apps.projects.models import Project, Proposition, Alternative, Tag


class PropositionInline(admin.TabularInline):
    model = Proposition


class ProjectAdmin(admin.ModelAdmin):
    inlines = [PropositionInline, ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Alternative)
admin.site.register(Tag)
