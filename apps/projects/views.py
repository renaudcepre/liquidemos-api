from django.shortcuts import render, get_object_or_404

from apps.projects.models.projects import Project


def list_projects(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', context={'projects': projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'project_detail.html', context={'project': project})
