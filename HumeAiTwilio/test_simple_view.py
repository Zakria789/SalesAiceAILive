"""
Simple test view to verify URL registration
"""
from django.http import JsonResponse

def test_simple_view(request):
    """Dead simple test view"""
    return JsonResponse({
        'status': 'OK',
        'message': 'This endpoint works!',
        'test': 'Simple view is accessible'
    })
