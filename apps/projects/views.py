from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from apps.projects.models import Project


class ProjectListView(ListView):
    paginate_by = 6
    model = Project
    ordering = ['created_at']

    def get_queryset(self):
        filter_by_tags = self.request.GET.get('tags')

        queryset = Project.objects.all()

        if filter_by_tags:
            queryset = queryset.filter(tags__name__in=filter_by_tags.split(','))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_by_tags = self.request.GET.get('tags', '')

        if filter_by_tags:
            context['filter_tags'] = filter_by_tags.split(',')
        return context


def project_detail(request, slug):
    """La vue d'un projet et toutes ses propositions liées, paginées."""
    project = get_object_or_404(Project, slug=slug)

    childs = project.childs(1)
    paginator = Paginator(childs, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'projects/project_detail.html',
                  context={'project': project,
                           'page_obj': page_obj,
                           'paginator': paginator})
