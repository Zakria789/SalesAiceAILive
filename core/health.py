"""
Health check endpoint for Railway deployment
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
@require_GET
def health_check(request):
    """
    Simple health check endpoint for Railway deployment
    Returns basic system status
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'SalesAI Live',
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'development'),
        'version': '1.0.0',
        'message': 'Service is running successfully'
    })

@csrf_exempt
@require_GET
def root_handler(request):
    """
    Root endpoint handler
    """
    return JsonResponse({
        'message': 'SalesAI Live - Voice AI Backend API',
        'status': 'active',
        'endpoints': {
            'api_docs': '/swagger/',
            'admin': '/admin/',
            'health': '/health/',
            'api_base': '/api/'
        }
    })