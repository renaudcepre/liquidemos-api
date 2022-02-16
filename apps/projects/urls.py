from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.projects.views import ProjectViewSet, ThemeViewSet, VoteAPIView

router = SimpleRouter()
router.register('projects', ProjectViewSet, 'project')
router.register('themes', ThemeViewSet, 'theme')

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<str:slug>/vote', VoteAPIView.as_view())
]
