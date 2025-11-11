"""
Quick test endpoint to debug analytics views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys

@api_view(['GET'])
def test_analytics_debug(request):
    """Test endpoint to debug analytics import issues"""
    
    debug_info = {
        'status': 'checking',
        'errors': [],
        'imported_views': []
    }
    
    # Test 1: Check if api_views package exists
    try:
        import HumeAiTwilio.api_views
        debug_info['api_views_package'] = 'EXISTS'
    except Exception as e:
        debug_info['errors'].append(f'api_views package error: {str(e)}')
        debug_info['api_views_package'] = 'MISSING'
    
    # Test 2: Check if analytics_views module can be imported
    try:
        from HumeAiTwilio.api_views import analytics_views
        debug_info['analytics_module'] = 'EXISTS'
    except Exception as e:
        debug_info['errors'].append(f'analytics_views module error: {str(e)}')
        debug_info['analytics_module'] = 'FAILED'
        return Response(debug_info)
    
    # Test 3: Check each view function
    views_to_check = [
        'conversation_metrics',
        'objection_types',
        'clarifies_flow_analysis',
        'win_loss_rate',
        'tone_trends',
        'call_explainability',
        'risk_flags_audit'
    ]
    
    for view_name in views_to_check:
        try:
            view_func = getattr(analytics_views, view_name)
            debug_info['imported_views'].append({
                'name': view_name,
                'type': str(type(view_func)),
                'status': 'OK'
            })
        except AttributeError as e:
            debug_info['errors'].append(f'{view_name}: {str(e)}')
            debug_info['imported_views'].append({
                'name': view_name,
                'status': 'MISSING'
            })
    
    # Test 4: Check models
    try:
        from HumeAiTwilio.models import (
            CallObjection,
            CLARIFIESStep,
            ConversationAnalytics,
            RiskFlag
        )
        debug_info['models'] = 'ALL_EXIST'
    except Exception as e:
        debug_info['errors'].append(f'Models import error: {str(e)}')
        debug_info['models'] = 'FAILED'
    
    debug_info['status'] = 'SUCCESS' if len(debug_info['errors']) == 0 else 'FAILED'
    
    return Response(debug_info)
