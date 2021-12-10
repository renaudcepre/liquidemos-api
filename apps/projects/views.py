from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from apps.projects.models import Project, Proposition


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
        context = super(ProjectListView, self).get_context_data(**kwargs)
        filter_by_tags = self.request.GET.get('tags', '')
        if filter_by_tags:
            context['filter_tags'] = filter_by_tags.split(',')
        return context


def project_detail(request, slug):
    """La vue d'un projet et toutes ses propositions liées, paginées."""
    project = get_object_or_404(Project, slug=slug)

    proposition_list = project.proposition_set.all().order_by('proposition__created_at')
    paginator = Paginator(proposition_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'projects/project_detail.html',
                  context={'project': project,
                           'page_obj': page_obj,
                           'paginator': paginator})


def proposition_detail(request, id):
    """La vue d'une proposition et toutes ses alternatives liées, paginées."""
    proposition = get_object_or_404(Proposition, pk=id)

    alernative_list = proposition.alternative_set.all().order_by('proposition__alternative')
    paginator = Paginator(alernative_list, 3)

    original_alt = proposition.alternative_set.order_by('created_by__alternative').first()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'projects/proposition_detail.html',
                  context={'proposition': proposition,
                           'original_alt': original_alt,
                           'page_obj': page_obj,
                           'paginator': paginator})
