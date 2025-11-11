"""
HumeAI + Twilio Intelligent Scheduling API
Customer response analysis aur automatic next call scheduling ke liye APIs
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import TwilioCall, HumeAgent, ConversationLog
from .intelligent_hume_scheduler import hume_twilio_scheduler
from agents.intelligent_response_scheduler import intelligent_scheduler
from agents.ai_agent_models import CustomerProfile, CallSession
from agents.auto_campaign_models import AutoCallCampaign

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_call_with_scheduling(request):
    """
    Initiate HumeAI call with intelligent scheduling setup
    Call ke saath automatic scheduling system ready karta hai
    """
    try:
        phone_number = request.data.get('phone_number')
        agent_id = request.data.get('agent_id')
        customer_name = request.data.get('customer_name', '')
        
        if not phone_number or not agent_id:
            return Response({
                'error': 'phone_number and agent_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get HumeAgent
        try:
            agent = HumeAgent.objects.get(id=agent_id)
        except HumeAgent.DoesNotExist:
            return Response({
                'error': 'HumeAgent not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create or get customer profile
        customer_profile, created = CustomerProfile.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'name': customer_name or f'Customer {phone_number}',
                'interest_level': 'warm',
                'call_preference_time': 'anytime'
            }
        )
        
        # Initiate call using existing HumeAI system
        from .twilio_voice_bridge import initiate_outbound_call
        
        call_result = initiate_outbound_call(phone_number, agent_id)
        
        if call_result['success']:
            return Response({
                'success': True,
                'message': 'Call initiated with intelligent scheduling ready',
                'call_sid': call_result['call_sid'],
                'customer_profile_id': customer_profile.id,
                'intelligent_scheduling': 'enabled'
            })
        else:
            return Response({
                'error': call_result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Failed to initiate call with scheduling: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_call_and_schedule(request):
    """
    Manually analyze completed call and trigger intelligent scheduling
    Completed call ko analyze kar ke next call schedule karta hai
    """
    try:
        call_sid = request.data.get('call_sid')
        force_outcome = request.data.get('outcome')  # Optional forced outcome
        
        if not call_sid:
            return Response({
                'error': 'call_sid is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get TwilioCall
        try:
            call = TwilioCall.objects.get(call_sid=call_sid)
        except TwilioCall.DoesNotExist:
            return Response({
                'error': 'Call not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Trigger intelligent scheduling
        scheduling_result = hume_twilio_scheduler.analyze_hume_call_and_schedule(
            call, 
            force_outcome=force_outcome
        )
        
        return Response({
            'success': True,
            'call_sid': call_sid,
            'analysis_result': scheduling_result
        })
        
    except Exception as e:
        logger.error(f"Failed to analyze call: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scheduling_stats(request):
    """
    Get intelligent scheduling statistics
    Scheduling system ke stats aur metrics show karta hai
    """
    try:
        # Get recent HumeAI calls with scheduling
        recent_calls = TwilioCall.objects.filter(
            status='completed',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('agent', 'analytics')
        
        # Calculate stats
        total_calls = recent_calls.count()
        calls_with_analytics = recent_calls.filter(analytics__isnull=False).count()
        
        # Outcome distribution
        outcomes = {}
        scheduled_calls = 0
        
        for call in recent_calls:
            if hasattr(call, 'analytics') and call.analytics:
                # Check conversation logs for outcome keywords
                conversation_logs = call.conversation_logs.filter(role='user')
                
                # Simple outcome detection
                outcome = 'unknown'
                for log in conversation_logs:
                    message = log.message.lower()
                    if any(word in message for word in ['yes', 'interested', 'sure']):
                        outcome = 'interested'
                        break
                    elif any(word in message for word in ['no', 'not interested']):
                        outcome = 'not_interested'
                        break
                    elif any(word in message for word in ['call back', 'later']):
                        outcome = 'callback_requested'
                        break
                
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
                
                # Check if follow-up was scheduled
                if outcome in ['interested', 'callback_requested', 'maybe_interested']:
                    scheduled_calls += 1
        
        # Get upcoming scheduled calls
        from django_celery_beat.models import PeriodicTask
        upcoming_tasks = PeriodicTask.objects.filter(
            name__startswith='auto_call_',
            enabled=True,
            one_off=True
        ).count()
        
        return Response({
            'success': True,
            'stats': {
                'total_completed_calls': total_calls,
                'calls_with_analytics': calls_with_analytics,
                'outcome_distribution': outcomes,
                'auto_scheduled_calls': scheduled_calls,
                'upcoming_scheduled_calls': upcoming_tasks,
                'scheduling_success_rate': f"{(scheduled_calls / total_calls * 100):.1f}%" if total_calls > 0 else "0%"
            },
            'time_period': '30 days'
        })
        
    except Exception as e:
        logger.error(f"Failed to get scheduling stats: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_intelligent_scheduling(request):
    """
    Test intelligent scheduling with sample data
    Testing ke liye sample call create kar ke scheduling test karta hai
    """
    try:
        # Create test scenario
        test_phone = request.data.get('test_phone', '+1234567890')
        test_outcome = request.data.get('test_outcome', 'interested')
        
        # Get or create test agent
        test_agent = HumeAgent.objects.filter(status='active').first()
        if not test_agent:
            return Response({
                'error': 'No active HumeAgent found for testing'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create test call
        test_call = TwilioCall.objects.create(
            agent=test_agent,
            call_sid=f'test_{timezone.now().timestamp()}',
            from_number='+1234567890',
            to_number=test_phone,
            status='completed',
            direction='outbound',
            duration=120,
            started_at=timezone.now() - timedelta(minutes=5),
            ended_at=timezone.now(),
            customer_name=f'Test Customer {test_phone}',
            customer_email='test@example.com'
        )
        
        # Create test conversation logs
        ConversationLog.objects.create(
            call=test_call,
            role='agent',
            message='Hello! I\'m calling about our special offer.',
            timestamp=timezone.now() - timedelta(minutes=4)
        )
        
        # Create customer response based on outcome
        customer_responses = {
            'interested': 'Yes, I\'m very interested! Tell me more about the pricing.',
            'callback_requested': 'This sounds good but I\'m busy right now. Can you call me back tomorrow?',
            'maybe_interested': 'Hmm, maybe. I need to think about it.',
            'not_interested': 'No thank you, I\'m not interested.',
            'no_answer': '',  # No customer response
            'busy': 'I\'m really busy right now, sorry!'
        }
        
        if test_outcome != 'no_answer':
            ConversationLog.objects.create(
                call=test_call,
                role='user',
                message=customer_responses.get(test_outcome, 'Ok'),
                timestamp=timezone.now() - timedelta(minutes=2)
            )
        
        # Test intelligent scheduling
        scheduling_result = hume_twilio_scheduler.analyze_hume_call_and_schedule(
            test_call,
            force_outcome=test_outcome
        )
        
        return Response({
            'success': True,
            'test_scenario': {
                'test_call_sid': test_call.call_sid,
                'test_phone': test_phone,
                'test_outcome': test_outcome,
                'customer_response': customer_responses.get(test_outcome, 'No response')
            },
            'scheduling_result': scheduling_result,
            'message': f'Test completed: {test_outcome} -> {scheduling_result.get("next_call_scheduled", False)}'
        })
        
    except Exception as e:
        logger.error(f"Failed to test intelligent scheduling: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_call_history(request):
    """
    Get call history and scheduling info for specific customer
    Customer ke call history aur scheduling details dikhata hai
    """
    try:
        phone_number = request.query_params.get('phone_number')
        
        if not phone_number:
            return Response({
                'error': 'phone_number parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all calls for this customer
        calls = TwilioCall.objects.filter(
            to_number=phone_number
        ).select_related('agent', 'analytics').order_by('-created_at')
        
        # Get customer profile
        try:
            customer_profile = CustomerProfile.objects.get(phone_number=phone_number)
        except CustomerProfile.DoesNotExist:
            customer_profile = None
        
        # Get scheduled calls
        from django_celery_beat.models import PeriodicTask
        scheduled_tasks = PeriodicTask.objects.filter(
            name__contains=phone_number.replace('+', ''),
            enabled=True
        )
        
        call_history = []
        for call in calls:
            # Get conversation summary
            conversation_logs = call.conversation_logs.all()
            
            call_info = {
                'call_sid': call.call_sid,
                'datetime': call.created_at,
                'duration': call.duration,
                'status': call.status,
                'agent_name': call.agent.name if call.agent else 'Unknown',
                'conversation_count': conversation_logs.count(),
                'has_analytics': hasattr(call, 'analytics') and call.analytics is not None
            }
            
            # Add analytics if available
            if hasattr(call, 'analytics') and call.analytics:
                call_info['analytics'] = {
                    'sentiment': call.analytics.overall_sentiment,
                    'lead_qualified': call.analytics.lead_qualified,
                    'summary': call.analytics.summary
                }
            
            call_history.append(call_info)
        
        return Response({
            'success': True,
            'phone_number': phone_number,
            'customer_profile': {
                'exists': customer_profile is not None,
                'name': customer_profile.name if customer_profile else None,
                'interest_level': customer_profile.interest_level if customer_profile else None
            },
            'call_history': call_history,
            'total_calls': len(call_history),
            'scheduled_calls': scheduled_tasks.count(),
            'next_scheduled_call': scheduled_tasks.first().start_time if scheduled_tasks.exists() else None
        })
        
    except Exception as e:
        logger.error(f"Failed to get customer call history: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)