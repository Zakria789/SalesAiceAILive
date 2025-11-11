"""
Dashboard API Views for HumeAI Twilio Integration
===================================================

Provides comprehensive dashboard APIs for:
1. Inbound Call Dashboard
2. Outbound Call Dashboard  
3. Analytics Dashboard
4. Bulk/Scheduled Calls Management
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F, Case, When
from django.db.models.functions import TruncDate, TruncHour

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import (
    TwilioCall, ConversationLog, CallAnalytics,
    HumeAgent, WebhookLog
)
from ..serializers import (
    TwilioCallSerializer, ConversationLogSerializer,
    CallAnalyticsSerializer
)

logger = logging.getLogger(__name__)


# ================================================================
# UNIFIED ACTIVE CALLS (BOTH INBOUND & OUTBOUND)
# ================================================================

@swagger_auto_schema(
    method='get',
    operation_description="""
    Get All Active and Completed Calls (Both Inbound & Outbound)
    
    Returns:
    - All active calls (ringing, in_progress) + completed calls
    - Type field to distinguish call direction (inbound/outbound)
    - Live transcripts with emotion/tone tags
    - Call duration in MINUTES
    - Call status and timestamps
    """,
    responses={
        200: openapi.Response(
            description="All active calls",
            examples={
                'application/json': {
                    'success': True,
                    'active_calls': [
                        {
                            'call_id': 'uuid',
                            'type': 'inbound',  # or 'outbound'
                            'from_number': '+1234567890',
                            'to_number': '+0987654321',
                            'status': 'in_progress',
                            'duration': 2.5,  # minutes
                            'recording_url': 'https://api.twilio.com/2010-04-01/Accounts/.../Recordings/....mp3',
                            'agent': {'id': 'uuid', 'name': 'Sales Agent'},
                            'live_transcript': [
                                {
                                    'role': 'user',
                                    'message': 'Hello, I need help',
                                    'emotion_scores': {'joy': 0.7, 'sadness': 0.1},
                                    'sentiment': 'positive',
                                    'timestamp': '2025-10-24T14:30:00Z'
                                }
                            ]
                        }
                    ],
                    'summary': {
                        'total_calls': 8,  # total returned
                        'total_active': 5,  # ringing + in_progress
                        'total_completed': 3,  # completed
                        'total_inbound': 5,
                        'total_outbound': 3,
                        'average_duration': 3.5,  # minutes
                        'longest_call': 10.25  # minutes
                    }
                }
            }
        )
    },
    tags=['Dashboard - Active Calls']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_active_calls(request):
    """Get all active and completed calls (both inbound and outbound) with live transcripts"""
    
    try:
        # Get ALL active AND completed calls (both inbound and outbound)
        # ✅ FILTER: Only Vonage provider calls
        # Include 'initiated' so newly created outbound calls appear immediately
        active_calls = TwilioCall.objects.filter(
            status__in=['ringing', 'initiated', 'completed'],
            provider='vonage'  # ✅ Only Vonage calls
        ).select_related('agent').order_by('-started_at')
        
        calls_data = []
        inbound_count = 0
        outbound_count = 0
        completed_count = 0
        active_count = 0
        
        for call in active_calls:
            # Get live transcript from local DB
            transcript = ConversationLog.objects.filter(
                call=call
            ).order_by('timestamp')
            
            transcript_data = []
            
            # If local transcript is empty, try to fetch from HumeAI (bypass errors)
            if not transcript.exists() and call.hume_session_id and call.agent:
                try:
                    import requests
                    from django.conf import settings
                    
                    # Fetch chat history from HumeAI
                    hume_api_key = settings.HUME_API_KEY
                    config_id = call.agent.hume_config_id
                    session_id = call.hume_session_id
                    
                    url = f"https://api.hume.ai/v0/evi/chat_events?config_id={config_id}&session_id={session_id}"
                    headers = {
                        "X-Hume-Api-Key": hume_api_key
                    }
                    
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        events = response.json().get('events', [])
                        
                        for event in events:
                            event_type = event.get('type')
                            
                            if event_type == 'user_message':
                                transcript_data.append({
                                    'role': 'user',
                                    'message': event.get('message', {}).get('content', ''),
                                    'emotion_scores': event.get('emotions', {}),
                                    'sentiment': None,
                                    'confidence': None,
                                    'timestamp': event.get('timestamp', '')
                                })
                            elif event_type == 'agent_message':
                                transcript_data.append({
                                    'role': 'assistant',
                                    'message': event.get('message', {}).get('content', ''),
                                    'emotion_scores': {},
                                    'sentiment': None,
                                    'confidence': None,
                                    'timestamp': event.get('timestamp', '')
                                })
                    else:
                        # Non-200 response, just continue with empty transcript
                        logger.warning(f"HumeAI API returned {response.status_code} for session {call.hume_session_id}, continuing with empty transcript")
                    
                except Exception as e:
                    # Any error (network, timeout, auth), bypass and continue with empty transcript
                    logger.warning(f"Failed to fetch HumeAI transcript for session {call.hume_session_id}: {str(e)}, continuing without transcript")
            
            # Use local transcript if available
            else:
                for log in transcript:
                    transcript_data.append({
                        'role': log.role,
                        'message': log.message,
                        'emotion_scores': log.emotion_scores or {},
                        'sentiment': log.sentiment,
                        'confidence': log.confidence,
                        'timestamp': log.timestamp.isoformat()
                    })
            
            # Calculate duration in minutes
            duration = 0
            
            # ✅ DATABASE-FIRST: Try to calculate from local timestamps
            if call.started_at:
                if call.ended_at:
                    # Completed call: use actual duration
                    duration_seconds = (call.ended_at - call.started_at).total_seconds()
                else:
                    # Active call: calculate from start to now
                    duration_seconds = (timezone.now() - call.started_at).total_seconds()
                duration = round(duration_seconds / 60, 2)  # Convert to minutes
            
            # ❌ TWILIO DURATION FETCH DISABLED - Using database only
            # # OLD TWILIO CODE (COMMENTED OUT - NO LONGER USING TWILIO)
            # elif duration == 0 and call.call_sid:
            #     try:
            #         from django.conf import settings
            #         from twilio.rest import Client
            #         
            #         # Initialize Twilio client
            #         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            #         
            #         # Fetch call details from Twilio
            #         twilio_call = client.calls(call.call_sid).fetch()
            #         
            #         # Get duration from Twilio (in seconds)
            #         if twilio_call.duration:
            #             duration = round(int(twilio_call.duration) / 60, 2)  # Convert to minutes
            #             
            #             # Update local database with timestamps if missing
            #             if not call.started_at and twilio_call.start_time:
            #                 call.started_at = twilio_call.start_time
            #             if not call.ended_at and twilio_call.end_time:
            #                 call.ended_at = twilio_call.end_time
            #             if not call.status:
            #                 call.status = twilio_call.status
            #             call.save(update_fields=['started_at', 'ended_at', 'status'])
            #         else:
            #             # Twilio returned no duration, just continue with 0
            #             logger.warning(f"Twilio returned no duration for call_sid {call.call_sid}, continuing with duration=0")
            #         
            #     except Exception as e:
            #         # Any error (network, auth, invalid SID), bypass and continue with duration=0
            #         logger.warning(f"Failed to fetch duration from Twilio for call_sid {call.call_sid}: {str(e)}, continuing with duration=0")
            
            # ❌ TWILIO RECORDING DISABLED - Using Vonage data from DB only
            # Fetch recording URL from database (Vonage saves it during call)
            recording_url = call.recording_url
            
            # # OLD TWILIO CODE (COMMENTED OUT - NO LONGER USING TWILIO)
            # if not recording_url and call.call_sid and call.status == 'completed':
            #     try:
            #         from django.conf import settings
            #         from twilio.rest import Client
            #         
            #         # Initialize Twilio client
            #         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            #         
            #         # Fetch recordings for this call
            #         recordings = client.recordings.list(call_sid=call.call_sid, limit=1)
            #         
            #         if recordings:
            #             # Get the recording URL (Twilio format: /2010-04-01/Accounts/{AccountSid}/Recordings/{RecordingSid})
            #             recording_sid = recordings[0].sid
            #             recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Recordings/{recording_sid}.mp3"
            #             
            #             # Save to local database for future use
            #             call.recording_url = recording_url
            #             call.save(update_fields=['recording_url'])
            #         
            #     except Exception as e:
            #         # Any error, bypass and continue without recording URL
            #         logger.warning(f"Failed to fetch recording URL from Twilio for call_sid {call.call_sid}: {str(e)}, continuing without recording")
            
            # Count by type
            if call.direction == 'inbound':
                inbound_count += 1
            else:
                outbound_count += 1
            
            # Count by status
            if call.status == 'completed':
                completed_count += 1
            else:
                active_count += 1
            
            calls_data.append({
                'call_id': str(call.id),
                'type': call.direction,  # 'inbound' or 'outbound'
                'call_sid': call.call_sid,
                'from_number': call.from_number,
                'to_number': call.to_number,
                'customer_name': call.customer_name or 'Unknown',
                'status': call.status,
                'duration': duration,
                'recording_url': recording_url,  # Audio recording URL from database (Vonage)
                'agent': {
                    'id': str(call.agent.id) if call.agent else None,
                    'name': call.agent.name if call.agent else 'No Agent'
                },
                'hume_session_id': call.hume_session_id,
                'live_transcript': transcript_data,
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None
            })
        
        # Summary statistics
        summary = {
            'total_calls': len(calls_data),
            'total_active': active_count,
            'total_completed': completed_count,
            'total_inbound': inbound_count,
            'total_outbound': outbound_count,
            'average_duration': round(sum(c['duration'] for c in calls_data) / len(calls_data), 2) if calls_data else 0,
            'longest_call': max([c['duration'] for c in calls_data]) if calls_data else 0
        }
        
        return Response({
            'success': True,
            'active_calls': calls_data,
            'summary': summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting all active calls: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================================================
# 1. INBOUND CALL DASHBOARD
# ================================================================

@swagger_auto_schema(
    method='get',
    operation_description="""
    Get Active Inbound Calls Dashboard
    
    Returns:
    - Active inbound calls with real-time status
    - Live transcripts with emotion/tone tags
    - Call duration and status
    """,
    responses={
        200: openapi.Response(
            description="Active inbound calls",
            examples={
                'application/json': {
                    'success': True,
                    'active_calls': [
                        {
                            'call_id': 'uuid',
                            'from_number': '+1234567890',
                            'to_number': '+0987654321',
                            'status': 'in_progress',
                            'duration': 120,
                            'agent': {'id': 'uuid', 'name': 'Sales Agent'},
                            'live_transcript': [
                                {
                                    'role': 'user',
                                    'message': 'Hello, I need help',
                                    'emotion_scores': {'joy': 0.7, 'sadness': 0.1},
                                    'sentiment': 'positive',
                                    'timestamp': '2025-10-24T14:30:00Z'
                                }
                            ]
                        }
                    ],
                    'summary': {
                        'total_active': 5,
                        'average_duration': 180,
                        'longest_call': 600
                    }
                }
            }
        )
    },
    tags=['Dashboard - Inbound']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_inbound_calls(request):
    """Get all active inbound calls with live transcripts"""
    
    try:
        # Get active inbound calls
        # ✅ FILTER: Only Vonage provider calls
        active_calls = TwilioCall.objects.filter(
            direction='inbound',
            status__in=['ringing', 'in_progress', 'initiated', 'completed'],
            provider='vonage'  # ✅ Only Vonage calls
        ).select_related('agent').order_by('-started_at')
        
        calls_data = []
        
        for call in active_calls:
            # Get live transcript
            transcript = ConversationLog.objects.filter(
                call=call
            ).order_by('timestamp')
            
            transcript_data = []
            for log in transcript:
                transcript_data.append({
                    'role': log.role,
                    'message': log.message,
                    'emotion_scores': log.emotion_scores or {},
                    'sentiment': log.sentiment,
                    'confidence': log.confidence,
                    'timestamp': log.timestamp.isoformat()
                })
            
            # Calculate duration in minutes
            duration = 0
            if call.started_at:
                duration_seconds = (timezone.now() - call.started_at).total_seconds()
                duration = round(duration_seconds / 60, 2)  # Convert to minutes
            
            calls_data.append({
                'call_id': str(call.id),
                'type': call.direction,  # 'inbound' or 'outbound'
                'call_sid': call.call_sid,
                'from_number': call.from_number,
                'to_number': call.to_number,
                'customer_name': call.customer_name or 'Unknown',
                'status': call.status,
                'duration': duration,
                'agent': {
                    'id': str(call.agent.id) if call.agent else None,
                    'name': call.agent.name if call.agent else 'No Agent'
                },
                'hume_session_id': call.hume_session_id,
                'live_transcript': transcript_data,
                'started_at': call.started_at.isoformat() if call.started_at else None
            })
        
        # Summary statistics
        summary = {
            'total_active': len(calls_data),
            'average_duration': sum(c['duration'] for c in calls_data) / len(calls_data) if calls_data else 0,
            'longest_call': max([c['duration'] for c in calls_data]) if calls_data else 0
        }
        
        return Response({
            'success': True,
            'active_calls': calls_data,
            'summary': summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting active inbound calls: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="""
    Get Inbound Call History
    
    Returns completed inbound calls with:
    - Full transcripts
    - Analytics and insights
    - Emotion/sentiment analysis
    - Call outcomes
    """,
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number'),
        openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Results per page'),
        openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter from date (YYYY-MM-DD)'),
        openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter to date (YYYY-MM-DD)'),
        openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Search by phone number or name'),
    ],
    tags=['Dashboard - Inbound']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_inbound_call_history(request):
    """Get completed inbound calls history"""
    
    try:
        # Base query - completed calls
        # ✅ FILTER: Only Vonage provider calls
        calls = TwilioCall.objects.filter(
            direction='inbound',
            status__in=['completed', 'failed', 'no_answer', 'busy'],
            provider='vonage'  # ✅ Only Vonage calls
        ).select_related('agent').prefetch_related('conversation_logs', 'analytics')
        
        # Apply filters
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        search = request.GET.get('search')
        
        if date_from:
            calls = calls.filter(started_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            calls = calls.filter(started_at__lte=datetime.strptime(date_to, '%Y-%m-%d'))
        if search:
            calls = calls.filter(
                Q(from_number__icontains=search) | Q(customer_name__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        total_count = calls.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        calls = calls.order_by('-ended_at')[start:end]
        
        # Build response
        calls_data = []
        for call in calls:
            # Get transcript
            transcript = call.conversation_logs.all()
            transcript_data = [{
                'role': log.role,
                'message': log.message,
                'emotion_scores': log.emotion_scores,
                'sentiment': log.sentiment,
                'timestamp': log.timestamp.isoformat()
            } for log in transcript]
            
            # Get analytics
            analytics_data = None
            if hasattr(call, 'analytics'):
                analytics = call.analytics
                analytics_data = {
                    'overall_sentiment': analytics.overall_sentiment,
                    'positive_score': analytics.positive_score,
                    'negative_score': analytics.negative_score,
                    'top_emotions': analytics.top_emotions,
                    'lead_qualified': analytics.lead_qualified,
                    'appointment_booked': analytics.appointment_booked,
                    'sale_made': analytics.sale_made,
                    'summary': analytics.summary
                }
            
            calls_data.append({
                'call_id': str(call.id),
                'call_sid': call.call_sid,
                'from_number': call.from_number,
                'to_number': call.to_number,
                'customer_name': call.customer_name,
                'status': call.status,
                'duration': call.duration,
                'agent': {
                    'id': str(call.agent.id) if call.agent else None,
                    'name': call.agent.name if call.agent else 'No Agent'
                },
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None,
                'transcript': transcript_data,
                'analytics': analytics_data,
                'recording_url': call.recording_url
            })
        
        return Response({
            'success': True,
            'calls': calls_data,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting inbound history: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================================================
# 2. OUTBOUND CALL DASHBOARD
# ================================================================

@swagger_auto_schema(
    method='post',
    operation_description="""
    Quick Call - Initiate Outbound Call
    
    Allows user to quickly call any number with selected agent
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone to call'),
            'agent_id': openapi.Schema(type=openapi.TYPE_STRING, description='Agent UUID'),
            'customer_name': openapi.Schema(type=openapi.TYPE_STRING, description='Customer name (optional)'),
        },
        required=['phone_number', 'agent_id']
    ),
    tags=['Dashboard - Outbound']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_outbound_call(request):
    """Quick call initiation"""
    
    try:
        phone_number = request.data.get('phone_number')
        agent_id = request.data.get('agent_id')
        customer_name = request.data.get('customer_name', '')
        
        if not phone_number or not agent_id:
            return Response({
                'success': False,
                'error': 'phone_number and agent_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get agent
        try:
            agent = HumeAgent.objects.get(id=agent_id)
        except HumeAgent.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agent not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create call record
        call = TwilioCall.objects.create(
            from_number='+12295152040',  # Your Twilio number
            to_number=phone_number,
            direction='outbound',
            status='initiated',
            agent=agent,
            user=request.user,
            customer_name=customer_name,
            started_at=timezone.now()
        )
        
        # TODO: Integrate with Twilio to actually initiate the call
        # For now, just create the record
        
        return Response({
            'success': True,
            'message': 'Call initiated',
            'call': {
                'call_id': str(call.id),
                'call_sid': call.call_sid,
                'phone_number': phone_number,
                'agent': agent.name,
                'status': call.status
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error initiating quick call: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="""
    Get Scheduled/Bulk Calls
    
    Returns list of:
    - Pending calls (waiting to be made)
    - Active calls (currently in progress)
    - Completed calls
    - Failed calls
    """,
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                         description='Filter by status: pending, in_progress, completed, failed'),
    ],
    tags=['Dashboard - Outbound']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scheduled_bulk_calls(request):
    """Get scheduled/bulk outbound calls"""
    
    try:
        # Get all outbound calls
        # ✅ FILTER: Only Vonage provider calls
        calls = TwilioCall.objects.filter(
            direction='outbound',
            provider='vonage'  # ✅ Only Vonage calls
        ).select_related('agent')
        
        # Filter by status if provided
        status_filter = request.GET.get('status')
        if status_filter:
            if status_filter == 'pending':
                calls = calls.filter(status='initiated')
            elif status_filter == 'in_progress':
                calls = calls.filter(status='in_progress')
            elif status_filter == 'completed':
                calls = calls.filter(status='completed')
            elif status_filter == 'failed':
                calls = calls.filter(status__in=['failed', 'no_answer', 'busy'])
        
        calls = calls.order_by('-created_at')
        
        # Group by status
        calls_data = {
            'pending': [],
            'active': [],
            'completed': [],
            'failed': []
        }
        
        for call in calls:
            call_info = {
                'call_id': str(call.id),
                'call_sid': call.call_sid,
                'to_number': call.to_number,
                'customer_name': call.customer_name,
                'status': call.status,
                'agent': {
                    'id': str(call.agent.id) if call.agent else None,
                    'name': call.agent.name if call.agent else 'No Agent'
                },
                'created_at': call.created_at.isoformat(),
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'duration': call.duration
            }
            
            if call.status == 'initiated':
                calls_data['pending'].append(call_info)
            elif call.status == 'in_progress':
                calls_data['active'].append(call_info)
            elif call.status == 'completed':
                calls_data['completed'].append(call_info)
            else:
                calls_data['failed'].append(call_info)
        
        # Summary
        summary = {
            'total_pending': len(calls_data['pending']),
            'total_active': len(calls_data['active']),
            'total_completed': len(calls_data['completed']),
            'total_failed': len(calls_data['failed'])
        }
        
        return Response({
            'success': True,
            'calls': calls_data,
            'summary': summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting scheduled/bulk calls: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="""
    Get Outbound Call History
    
    Shows all completed outbound calls with:
    - Call outcomes
    - Transcripts
    - Analytics
    """,
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING),
    ],
    tags=['Dashboard - Outbound']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_outbound_call_history(request):
    """Get outbound call history - similar to inbound but for outbound"""
    
    try:
        # ✅ FILTER: Only Vonage provider calls
        calls = TwilioCall.objects.filter(
            direction='outbound',
            status__in=['completed', 'failed', 'no_answer', 'busy'],
            provider='vonage'  # ✅ Only Vonage calls
        ).select_related('agent').prefetch_related('conversation_logs', 'analytics')
        
        # Apply filters (date, search, etc.)
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if date_from:
            calls = calls.filter(started_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            calls = calls.filter(started_at__lte=datetime.strptime(date_to, '%Y-%m-%d'))
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        total_count = calls.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        calls = calls.order_by('-ended_at')[start:end]
        
        # Build response (similar to inbound history)
        calls_data = []
        for call in calls:
            transcript = call.conversation_logs.all()
            transcript_data = [{
                'role': log.role,
                'message': log.message,
                'emotion_scores': log.emotion_scores,
                'sentiment': log.sentiment,
                'timestamp': log.timestamp.isoformat()
            } for log in transcript]
            
            analytics_data = None
            if hasattr(call, 'analytics'):
                analytics = call.analytics
                analytics_data = {
                    'overall_sentiment': analytics.overall_sentiment,
                    'positive_score': analytics.positive_score,
                    'top_emotions': analytics.top_emotions,
                    'lead_qualified': analytics.lead_qualified,
                    'sale_made': analytics.sale_made,
                    'summary': analytics.summary
                }
            
            calls_data.append({
                'call_id': str(call.id),
                'to_number': call.to_number,
                'customer_name': call.customer_name,
                'status': call.status,
                'duration': call.duration,
                'agent': {
                    'id': str(call.agent.id) if call.agent else None,
                    'name': call.agent.name if call.agent else None
                },
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None,
                'transcript': transcript_data,
                'analytics': analytics_data
            })
        
        return Response({
            'success': True,
            'calls': calls_data,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting outbound history: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================================================
# 3. ANALYTICS DASHBOARD
# ================================================================

@swagger_auto_schema(
    method='get',
    operation_description="""
    Get Analytics Dashboard
    
    Comprehensive analytics including:
    - Sentiment trends over time
    - Average emotions
    - Call volume trends
    - Success metrics
    - Agent performance
    """,
    manual_parameters=[
        openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                         description='Start date (YYYY-MM-DD), default: 7 days ago'),
        openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                         description='End date (YYYY-MM-DD), default: today'),
        openapi.Parameter('agent_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                         description='Filter by specific agent'),
    ],
    tags=['Dashboard - Analytics']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_dashboard(request):
    """Get comprehensive analytics dashboard"""
    
    try:
        # Date range
        date_to = request.GET.get('date_to', timezone.now().date())
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        date_from = request.GET.get('date_from')
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            date_from = date_to - timedelta(days=7)
        
        # Filter analytics
        analytics = CallAnalytics.objects.filter(
            call__started_at__date__gte=date_from,
            call__started_at__date__lte=date_to
        ).select_related('call', 'call__agent')
        
        # Filter by agent if specified
        agent_id = request.GET.get('agent_id')
        if agent_id:
            analytics = analytics.filter(call__agent_id=agent_id)
        
        # 1. Sentiment Trend Over Time
        sentiment_trend = (
            analytics
            .annotate(date=TruncDate('call__started_at'))
            .values('date')
            .annotate(
                avg_positive=Avg('positive_score'),
                avg_negative=Avg('negative_score'),
                avg_neutral=Avg('neutral_score'),
                count=Count('id')
            )
            .order_by('date')
        )
        
        sentiment_data = []
        for item in sentiment_trend:
            sentiment_data.append({
                'date': item['date'].isoformat(),
                'positive': round(item['avg_positive'] or 0, 2),
                'negative': round(item['avg_negative'] or 0, 2),
                'neutral': round(item['avg_neutral'] or 0, 2),
                'call_count': item['count']
            })
        
        # 2. Overall Metrics
        total_calls = analytics.count()
        avg_positive = analytics.aggregate(Avg('positive_score'))['positive_score__avg'] or 0
        avg_negative = analytics.aggregate(Avg('negative_score'))['negative_score__avg'] or 0
        
        overall_metrics = {
            'total_calls': total_calls,
            'avg_positive_sentiment': round(avg_positive, 2),
            'avg_negative_sentiment': round(avg_negative, 2),
            'leads_qualified': analytics.filter(lead_qualified=True).count(),
            'appointments_booked': analytics.filter(appointment_booked=True).count(),
            'sales_made': analytics.filter(sale_made=True).count()
        }
        
        # 3. Top Emotions Analysis
        all_emotions = {}
        for analytic in analytics:
            if analytic.top_emotions:
                for emotion, score in analytic.top_emotions.items():
                    if emotion not in all_emotions:
                        all_emotions[emotion] = []
                    all_emotions[emotion].append(score)
        
        emotion_summary = []
        for emotion, scores in all_emotions.items():
            emotion_summary.append({
                'emotion': emotion,
                'avg_score': round(sum(scores) / len(scores), 2),
                'occurrences': len(scores)
            })
        
        emotion_summary.sort(key=lambda x: x['avg_score'], reverse=True)
        
        # 4. Call Volume by Hour
        call_volume = (
            TwilioCall.objects.filter(
                started_at__date__gte=date_from,
                started_at__date__lte=date_to
            )
            .annotate(hour=TruncHour('started_at'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )
        
        volume_data = [{
            'hour': item['hour'].isoformat(),
            'call_count': item['count']
        } for item in call_volume]
        
        # 5. Agent Performance
        agent_performance = (
            analytics
            .values('call__agent__id', 'call__agent__name')
            .annotate(
                total_calls=Count('id'),
                avg_sentiment=Avg('positive_score'),
                leads_qualified=Count('id', filter=Q(lead_qualified=True)),
                sales_made=Count('id', filter=Q(sale_made=True))
            )
            .order_by('-total_calls')
        )
        
        agent_data = []
        for agent in agent_performance:
            agent_data.append({
                'agent_id': str(agent['call__agent__id']) if agent['call__agent__id'] else None,
                'agent_name': agent['call__agent__name'] or 'No Agent',
                'total_calls': agent['total_calls'],
                'avg_sentiment': round(agent['avg_sentiment'] or 0, 2),
                'leads_qualified': agent['leads_qualified'],
                'sales_made': agent['sales_made']
            })
        
        return Response({
            'success': True,
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'overall_metrics': overall_metrics,
            'sentiment_trend': sentiment_data,
            'top_emotions': emotion_summary[:10],  # Top 10
            'call_volume_by_hour': volume_data,
            'agent_performance': agent_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================================================
# 4. BULK/SCHEDULED CALLS MANAGEMENT
# ================================================================

@swagger_auto_schema(
    method='post',
    operation_description="""
    Upload CSV for Bulk Calls
    
    CSV Format:
    phone_number,customer_name,notes
    +1234567890,John Doe,High priority lead
    +0987654321,Jane Smith,Follow up call
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'csv_file': openapi.Schema(type=openapi.TYPE_FILE, description='CSV file with contacts'),
            'agent_id': openapi.Schema(type=openapi.TYPE_STRING, description='Agent UUID'),
            'schedule_time': openapi.Schema(type=openapi.TYPE_STRING, 
                                           description='Schedule for later (ISO datetime) or immediate'),
        },
        required=['csv_file', 'agent_id']
    ),
    tags=['Dashboard - Bulk Calls']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_bulk_calls_csv(request):
    """Upload CSV file to schedule bulk calls"""
    
    try:
        import csv
        import io
        
        csv_file = request.FILES.get('csv_file')
        agent_id = request.data.get('agent_id')
        schedule_time = request.data.get('schedule_time')
        
        if not csv_file or not agent_id:
            return Response({
                'success': False,
                'error': 'csv_file and agent_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get agent
        try:
            agent = HumeAgent.objects.get(id=agent_id)
        except HumeAgent.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agent not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse CSV
        decoded_file = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_file))
        
        created_calls = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                phone_number = row.get('phone_number', '').strip()
                customer_name = row.get('customer_name', '').strip()
                notes = row.get('notes', '').strip()
                
                if not phone_number:
                    errors.append({
                        'row': row_num,
                        'error': 'Missing phone_number'
                    })
                    continue
                
                # Create call record
                call = TwilioCall.objects.create(
                    from_number='+12295152040',
                    to_number=phone_number,
                    direction='outbound',
                    status='initiated',  # Will be picked up by scheduler
                    agent=agent,
                    user=request.user,
                    customer_name=customer_name
                )
                
                created_calls.append({
                    'call_id': str(call.id),
                    'phone_number': phone_number,
                    'customer_name': customer_name
                })
                
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'message': f'Bulk calls created successfully',
            'created_count': len(created_calls),
            'error_count': len(errors),
            'created_calls': created_calls,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error uploading bulk calls: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_summary="Get Live Call Updates",
    operation_description="""
    Real-time endpoint for frontend polling during active calls.
    Returns ONLY in-progress calls with latest transcript updates.
    
    Frontend should poll this every 2-3 seconds during active calls.
    """,
    responses={
        200: openapi.Response(
            description="Live call data",
            examples={
                'application/json': {
                    'success': True,
                    'live_calls': [
                        {
                            'call_id': 'uuid',
                            'status': 'in_progress',
                            'duration': 1.5,
                            'latest_transcript': [
                                {
                                    'role': 'user',
                                    'message': 'Hello',
                                    'timestamp': '2025-11-04T12:00:00Z'
                                }
                            ],
                            'agent_status': 'active'
                        }
                    ],
                    'count': 1
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_live_call_updates(request):
    """
    🔴 LIVE UPDATES ENDPOINT
    
    Frontend polling endpoint for real-time call updates.
    Returns only IN-PROGRESS calls with latest transcript.
    """
    
    try:
        # Get ACTIVE calls for live updates
        # ✅ FILTER: Only Vonage provider + in_progress OR initiated (for outbound)
        # Include 'initiated' to show outbound calls immediately after creation
        live_calls = TwilioCall.objects.filter(
            status__in=['in_progress'],  # ✅ Include initiated/ringing calls
            provider='vonage'
        ).select_related('agent').order_by('-started_at')  # Most recent first

        logger.info(f"📊 Live updates: {live_calls.count()} active calls (in_progress/ringing)")

        calls_data = []
        
        for call in live_calls:
            # Get latest 10 transcript entries
            latest_transcript = ConversationLog.objects.filter(
                call=call
            ).order_by('-timestamp')[:10]
            
            transcript_data = []
            for log in reversed(latest_transcript):  # Reverse to show oldest first
                transcript_data.append({
                    'role': log.role,
                    'message': log.message,
                    'emotion_scores': log.emotion_scores or {},
                    'sentiment': log.sentiment,
                    'confidence': log.confidence,
                    'timestamp': log.timestamp.isoformat()
                })
            
            # Calculate live duration
            duration = 0
            if call.started_at:
                duration_seconds = (timezone.now() - call.started_at).total_seconds()
                duration = round(duration_seconds / 60, 2)
            
            calls_data.append({
                'call_id': str(call.id),
                'call_sid': call.call_sid,
                'from_number': call.from_number,
                'to_number': call.to_number,
                'customer_name': call.customer_name or 'Unknown',
                'direction': call.direction,  # ✅ Add direction field
                'status': call.status,
                'duration': duration,  # Live duration in minutes
                'agent': {
                    'id': str(call.agent.id) if call.agent else None,
                    'name': call.agent.name if call.agent else 'No Agent',
                    'status': call.agent.status if call.agent else 'unknown'
                },
                'hume_session_id': call.hume_session_id,
                'latest_transcript': transcript_data,  # Latest 10 messages
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'transcript_count': ConversationLog.objects.filter(call=call).count()
            })
        
        return Response({
            'success': True,
            'live_calls': calls_data,
            'count': len(calls_data),
            'timestamp': timezone.now().isoformat()  # For frontend sync
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting live call updates: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
