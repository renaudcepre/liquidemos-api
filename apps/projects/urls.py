from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.projects.views import ProjectViewSet, ThemeViewSet

router = SimpleRouter()
router.register('projects', ProjectViewSet, 'project')
router.register('themes', ThemeViewSet, 'theme')

urlpatterns = [
    path('', include(router.urls)),
]
