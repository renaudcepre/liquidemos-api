from typing import Optional

from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from apps.projects.models import Project


class ProjectListView(ListView):
    paginate_by = 6
    model = Project
    ordering = ['created_at']

    def get_queryset(self):
        filter_by_tags = self.request.GET.get('tags')
        filter_by_childs_of = self.request.GET.get('childs_of')

        queryset: Optional[QuerySet] = None
        if filter_by_childs_of:
            project = get_object_or_404(Project, slug=filter_by_childs_of)
            queryset = project.childs()
        else:
            queryset = Project.objects.all()

        if filter_by_tags:
            queryset = queryset.filter(tags__name__in=filter_by_tags.split(','))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_by_tags = self.request.GET.get('tags', '')
        filter_by_childs_of = self.request.GET.get('childs_of')

        if filter_by_tags:
            context['filter_tags'] = filter_by_tags.split(',')
        if filter_by_childs_of:
            context['childs_of'] = get_object_or_404(Project, slug=filter_by_childs_of)
        return context


def project_detail(request, slug):
    """La vue d'un projet et toutes ses propositions liées, paginées."""
    project = get_object_or_404(Project, slug=slug)

    return render(request, 'projects/project_detail.html',
                  context={'project': project})
