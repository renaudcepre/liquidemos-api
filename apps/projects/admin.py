from django.contrib import admin

from apps.projects.models import Project, Tag, AlternativeGroup, Vote


class TagListFilter(admin.SimpleListFilter):
    title = 'tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        tag_list = []
        for tag in Tag.objects.all():
            tag_list.append((tag.name, tag.name))
        return tag_list

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is not None:
            return queryset.filter(tags__name=self.value())
        return queryset


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "created_by",
        "depth",
        "upvotes",
    )
    ordering = ("depth", "parent",)
    search_fields = ("name",)
    list_filter = (TagListFilter,)
    autocomplete_fields = ('created_by', 'depends_on', 'parent')
    filter_horizontal = ('tags',)


admin.site.register(Tag)
admin.site.register(AlternativeGroup)
admin.site.register(Vote)
