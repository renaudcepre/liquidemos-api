"""liquidemos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.projects.urls import router as projects_router
from liquidemos import settings

router = DefaultRouter()
# router.registry.extend(users_router.registry)
router.registry.extend(projects_router.registry)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls'))

]

if settings.DEBUG:
    urlpatterns += [
        # DRF Browsable-api login / logout
        path('api-auth/', include('rest_framework.urls')),
        # debug toolbar
        path('__debug__/', include('debug_toolbar.urls')),
    ]
