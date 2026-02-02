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
from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path

from lims.views import user_views 
from lims.views import alert_views
from lims.views import  notification_views
from lims.views import sensor_views

urlpatterns = [
    # ... your existing job/client urls ...
 path('api/', include('lims.urls.system_urls')),

   path('auth/register/', user_views.register_user, name='register'),
    path('auth/login/', user_views.MyTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile
    path('auth/me/', user_views.current_user, name='current_user'),
    # Organization URLs
    path('organizations/', views.organization_list_create, name='organization-list-create'),
    path('organizations/<int:pk>/', views.organization_detail, name='organization-detail'),

    # Zone URLs
    path('zones/', views.zone_list_create, name='zone-list-create'),
    path('zones/<int:pk>/', views.zone_detail, name='zone-detail'),

    # Camera URLs
    path('cameras/', views.camera_list_create, name='camera-list-create'),
    path('cameras/<int:pk>/', views.camera_detail, name='camera-detail'),

    path('alerts/', alert_views.alert_list_create, name='alert-list-create'),
    path('alerts/<int:pk>/', alert_views.alert_detail, name='alert-detail'),

    path('notifications/', notification_views.notification_list_create, name='notification-list-create'),

    # Get one (GET) or Delete (DELETE)
    path('notifications/<int:pk>/', notification_views.notification_detail, name='notification-detail'),

    path('sensor/detect/', sensor_views.sensor_detect, name='sensor-detect'),
    path('carbon/stats/', sensor_views.get_carbon_stats, name='get-carbon-stats'),
]