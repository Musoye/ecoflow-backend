from django.urls import path
from ..views.system_views import system_status, system_health

urlpatterns = [
    path("status/", system_status, name="system_status"),
    path("health/", system_health, name="system_health"),
]