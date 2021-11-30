from django.urls import path

from apps.projects.views import list_projects, project_detail

urlpatterns = [
    path('', list_projects),
    path('<str:slug>', project_detail),
]