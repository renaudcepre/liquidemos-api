from django.urls import path

from apps.projects.views import ProjectListCreateAPIView, ProjectDetail

urlpatterns = [
    path('', ProjectListCreateAPIView.as_view(), name='projects'),
    path('<str:slug>/', ProjectDetail.as_view(), name='project_detail'),
]
