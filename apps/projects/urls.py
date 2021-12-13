from django.urls import path

from apps.projects.views import ProjectListView, project_detail

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    path('<str:slug>', project_detail, name='project_detail'),
]
