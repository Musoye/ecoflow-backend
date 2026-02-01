"""
URL configuration for kazlat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include


from django.urls import path
from lims.views import views

urlpatterns = [
    # ... your existing job/client urls ...
 path('api/', include('lims.urls.system_urls')),
    # Organization URLs
    path('organizations/', views.organization_list_create, name='organization-list-create'),
    path('organizations/<int:pk>/', views.organization_detail, name='organization-detail'),

    # Zone URLs
    path('zones/', views.zone_list_create, name='zone-list-create'),
    path('zones/<int:pk>/', views.zone_detail, name='zone-detail'),

    # Camera URLs
    path('cameras/', views.camera_list_create, name='camera-list-create'),
    path('cameras/<int:pk>/', views.camera_detail, name='camera-detail'),
]