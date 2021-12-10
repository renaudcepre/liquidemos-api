from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from apps.projects.models import Project, Proposition


class ProjectListView(ListView):
    paginate_by = 6
    model = Project
    ordering = ['created_at']


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
    proposition = get_object_or_404(Proposition, pk=id)
    return render(request, 'projects/proposition_detail.html',
                  context={'proposition': proposition})
