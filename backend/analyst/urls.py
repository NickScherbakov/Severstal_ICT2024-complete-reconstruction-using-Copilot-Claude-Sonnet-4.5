from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse


def health_check(request):
    """
    Health check endpoint for Kubernetes liveness probe
    """
    return JsonResponse({'status': 'healthy'})


def ready_check(request):
    """
    Readiness check endpoint for Kubernetes readiness probe
    Checks database and message broker connectivity
    """
    from analytics.monitoring import HealthCheck
    
    status = HealthCheck.get_health_status()
    http_status = 200 if status['status'] == 'healthy' else 503
    
    return JsonResponse(status, status=http_status)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('health/', health_check, name='health_check'),
    path('ready/', ready_check, name='ready_check'),
]
