"""
Test analytics views WITHOUT authentication - for debugging
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
import logging

from HumeAiTwilio.models import (
    ConversationAnalytics,
    CallObjection,
    CLARIFIESStep,
    RiskFlag
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
def test_conversation_metrics(request):
    """Test endpoint WITHOUT authentication"""
    try:
        total_calls = ConversationAnalytics.objects.count()
        
        return Response({
            'success': True,
            'message': 'Analytics endpoint working!',
            'total_calls_analyzed': total_calls,
            'test': 'This endpoint works WITHOUT authentication'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def test_objection_types(request):
    """Test endpoint WITHOUT authentication"""
    try:
        total_objections = CallObjection.objects.count()
        
        return Response({
            'success': True,
            'message': 'Objections endpoint working!',
            'total_objections': total_objections
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
