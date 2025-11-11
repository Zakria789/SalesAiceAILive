"""
Views for HumeAI + Twilio Integration
API endpoints for managing agents, calls, and webhooks
"""

import json
import logging
from typing import Dict, Any

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import (
    HumeAgent, TwilioCall, ConversationLog,
    CallAnalytics, WebhookLog
)
from .serializers import (
    HumeAgentSerializer, TwilioCallSerializer, TwilioCallListSerializer,
    ConversationLogSerializer, CallAnalyticsSerializer,
    WebhookLogSerializer, InitiateCallSerializer
)
from .services import (
    TwilioService, HumeAIService, ConversationService,
    AnalyticsService, WebhookService
)
from .hume_agent_service import hume_agent_service

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HumeAgentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing HumeAI Agents
    
    Endpoints:
    - GET /api/hume-agents/ - List all agents
    - POST /api/hume-agents/ - Create new agent
    - GET /api/hume-agents/{id}/ - Get agent details
    - PUT /api/hume-agents/{id}/ - Update agent
    - DELETE /api/hume-agents/{id}/ - Delete agent
    - GET /api/hume-agents/{id}/performance/ - Get agent performance metrics
    """
    
    queryset = HumeAgent.objects.all()
    serializer_class = HumeAgentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create agent locally and sync with HumeAI"""
        agent = serializer.save(created_by=self.request.user)
        
        # Directly call HumeAI API to create agent
        try:
            config_id = hume_agent_service.create_agent(
                name=agent.name,
                system_prompt=agent.system_prompt,
                voice_name=agent.voice_name,
                language=agent.language
            )
            
            if config_id:
                agent.hume_config_id = config_id
                agent.save(update_fields=['hume_config_id'])
                logger.info(f"✅ Agent '{agent.name}' synced to HumeAI with config_id: {config_id}")
            else:
                logger.warning(f"⚠️ Agent '{agent.name}' created locally but HumeAI sync failed")
                
        except Exception as e:
            logger.error(f"❌ Error syncing agent to HumeAI: {str(e)}")
            # Agent still exists locally, just without HumeAI config_id
    
    def perform_update(self, serializer):
        """Update agent locally and sync with HumeAI"""
        agent = serializer.save()
        
        # If agent has HumeAI config, update it there too
        if agent.hume_config_id:
            try:
                success = hume_agent_service.update_agent(
                    config_id=agent.hume_config_id,
                    data={
                        'name': agent.name,
                        'system_prompt': agent.system_prompt,
                        'voice': {'name': agent.voice_name},
                        'language': agent.language
                    }
                )
                
                if success:
                    logger.info(f"✅ Agent '{agent.name}' updated in HumeAI")
                else:
                    logger.warning(f"⚠️ Agent '{agent.name}' updated locally but HumeAI sync failed")
                    
            except Exception as e:
                logger.error(f"❌ Error updating agent in HumeAI: {str(e)}")
    
    def perform_destroy(self, instance):
        """Delete agent from HumeAI before deleting locally"""
        if instance.hume_config_id:
            try:
                success = hume_agent_service.delete_agent(instance.hume_config_id)
                if success:
                    logger.info(f"✅ Agent '{instance.name}' deleted from HumeAI")
                else:
                    logger.warning(f"⚠️ Failed to delete agent from HumeAI")
            except Exception as e:
                logger.error(f"❌ Error deleting agent from HumeAI: {str(e)}")
        
        # Delete from local database
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance metrics for this agent"""
        agent = self.get_object()
        days = int(request.query_params.get('days', 30))
        
        performance_data = AnalyticsService.get_agent_performance(agent, days)
        
        return Response(performance_data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an agent"""
        agent = self.get_object()
        agent.status = 'active'
        agent.save()
        
        return Response({
            'message': f'Agent {agent.name} activated successfully',
            'status': agent.status
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an agent"""
        agent = self.get_object()
        agent.status = 'inactive'
        agent.save()
        
        return Response({
            'message': f'Agent {agent.name} deactivated successfully',
            'status': agent.status
        })


class TwilioCallViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Twilio Calls
    
    Endpoints:
    - GET /api/calls/ - List all calls
    - POST /api/calls/ - Initiate new call
    - GET /api/calls/{id}/ - Get call details
    - GET /api/calls/{id}/conversation/ - Get conversation logs
    - GET /api/calls/{id}/analytics/ - Get call analytics
    - POST /api/calls/{id}/terminate/ - Terminate active call
    """
    
    queryset = TwilioCall.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TwilioCallListSerializer
        return TwilioCallSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by agent
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        
        # Filter by direction
        direction = self.request.query_params.get('direction', None)
        if direction:
            queryset = queryset.filter(direction=direction)
        
        # Search by phone number
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(from_number__icontains=search) | 
                Q(to_number__icontains=search) |
                Q(customer_name__icontains=search)
            )
        
        return queryset.select_related('agent', 'user')
    
    def create(self, request, *args, **kwargs):
        """Initiate a new outbound call"""
        serializer = InitiateCallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        to_number = serializer.validated_data['to_number']
        agent_id = serializer.validated_data['agent_id']
        customer_name = serializer.validated_data.get('customer_name', '')
        customer_email = serializer.validated_data.get('customer_email', '')
        
        try:
            agent = HumeAgent.objects.get(id=agent_id, status='active')
        except HumeAgent.DoesNotExist:
            return Response(
                {'error': 'Agent not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Initialize Twilio service
        twilio_service = TwilioService()
        
        # Generate callback URL
        callback_url = request.build_absolute_uri('/api/hume-twilio/webhooks/twilio')
        
        # Initiate call
        result = twilio_service.initiate_call(
            to_number=to_number,
            agent=agent,
            callback_url=callback_url
        )
        
        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Failed to initiate call')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create call record
        call = TwilioCall.objects.create(
            call_sid=result['call_sid'],
            from_number=twilio_service.phone_number,
            to_number=to_number,
            direction='outbound',
            status='initiated',
            agent=agent,
            user=request.user,
            customer_name=customer_name,
            customer_email=customer_email
        )
        
        response_serializer = TwilioCallSerializer(call)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def conversation(self, request, pk=None):
        """Get conversation logs for a call"""
        call = self.get_object()
        logs = call.conversation_logs.all()
        serializer = ConversationLogSerializer(logs, many=True)
        
        return Response({
            'call_id': str(call.id),
            'call_sid': call.call_sid,
            'total_messages': logs.count(),
            'messages': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a call"""
        call = self.get_object()
        
        # Calculate analytics if not exists
        if not hasattr(call, 'analytics'):
            analytics = AnalyticsService.calculate_analytics(call)
        else:
            analytics = call.analytics
        
        serializer = CallAnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate an active call"""
        call = self.get_object()
        
        if call.status not in ['initiated', 'ringing', 'in_progress']:
            return Response(
                {'error': 'Call is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        twilio_service = TwilioService()
        success = twilio_service.terminate_call(call.call_sid)
        
        if success:
            call.status = 'canceled'
            call.ended_at = timezone.now()
            call.save()
            
            return Response({'message': 'Call terminated successfully'})
        else:
            return Response(
                {'error': 'Failed to terminate call'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete_with_outcome(self, request, pk=None):
        """
        Complete call with specified outcome for intelligent scheduling
        🚀 API endpoint to manually trigger intelligent scheduling
        """
        call = self.get_object()
        outcome = request.data.get('outcome')
        
        valid_outcomes = ['interested', 'callback_requested', 'maybe_interested', 'not_interested', 'no_answer', 'busy']
        
        if outcome not in valid_outcomes:
            return Response(
                {'error': f'Invalid outcome. Must be one of: {valid_outcomes}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark call as completed
        if call.status != 'completed':
            call.status = 'completed'
            call.ended_at = timezone.now()
            call.save()
        
        # Trigger intelligent scheduling with forced outcome
        from .intelligent_hume_scheduler import hume_twilio_scheduler
        
        try:
            scheduling_result = hume_twilio_scheduler.analyze_hume_call_and_schedule(
                call, 
                force_outcome=outcome
            )
            
            return Response({
                'message': f'Call completed with outcome: {outcome}',
                'intelligent_scheduling': scheduling_result
            })
            
        except Exception as e:
            return Response(
                {'error': f'Scheduling failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing conversation logs
    """
    queryset = ConversationLog.objects.all()
    serializer_class = ConversationLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by call
        call_id = self.request.query_params.get('call_id', None)
        if call_id:
            queryset = queryset.filter(call_id=call_id)
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset.select_related('call')


class CallAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing call analytics
    """
    queryset = CallAnalytics.objects.all()
    serializer_class = CallAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


# Webhook Endpoints

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def twilio_webhook(request):
    """
    Twilio webhook endpoint
    Handles call status updates, recordings, etc.
    """
    try:
        payload = request.POST.dict()
        headers = dict(request.headers)
        
        # Log webhook
        WebhookService.log_webhook(
            source='twilio',
            event_type=payload.get('CallStatus', 'unknown'),
            payload=payload,
            headers=headers
        )
        
        # Process webhook
        result = WebhookService.process_twilio_webhook(payload)
        
        if result.get('success'):
            return HttpResponse(status=200)
        else:
            logger.error(f"Webhook processing failed: {result.get('error')}")
            return HttpResponse(status=200)  # Still return 200 to Twilio
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=200)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def twilio_twiml(request):
    """
    Generate TwiML response for incoming/outgoing calls
    """
    try:
        call_sid = request.POST.get('CallSid')
        
        # Find the call
        call = TwilioCall.objects.filter(call_sid=call_sid).first()
        
        if not call or not call.agent:
            # Default response
            from twilio.twiml.voice_response import VoiceResponse
            response = VoiceResponse()
            response.say('Sorry, no agent is available at this time.')
            return HttpResponse(str(response), content_type='text/xml')
        
        # Generate WebSocket URL for streaming
        websocket_url = request.build_absolute_uri('/ws/hume-twilio/stream/')
        
        # Generate TwiML
        twilio_service = TwilioService()
        twiml = twilio_service.generate_twiml_response(call.agent, websocket_url)
        
        return HttpResponse(twiml, content_type='text/xml')
    
    except Exception as e:
        logger.error(f"TwiML generation error: {str(e)}")
        from twilio.twiml.voice_response import VoiceResponse
        response = VoiceResponse()
        response.say('An error occurred. Please try again later.')
        return HttpResponse(str(response), content_type='text/xml')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def hume_webhook(request):
    """
    HumeAI webhook endpoint
    Handles emotion events, conversation updates, etc.
    """
    try:
        payload = request.data
        headers = dict(request.headers)
        
        # Log webhook
        WebhookService.log_webhook(
            source='hume',
            event_type=payload.get('event_type', 'unknown'),
            payload=payload,
            headers=headers
        )
        
        # Process HumeAI webhook
        # Add your HumeAI webhook processing logic here
        
        return Response({'status': 'received'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"HumeAI webhook error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_200_OK)


# Dashboard & Analytics Endpoints

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics
    """
    try:
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Total calls
        total_calls = TwilioCall.objects.filter(created_at__gte=start_date).count()
        
        # Calls by status
        calls_by_status = TwilioCall.objects.filter(
            created_at__gte=start_date
        ).values('status').annotate(count=Count('id'))
        
        # Total duration
        total_duration = TwilioCall.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).aggregate(total=Sum('duration'))['total'] or 0
        
        # Active agents
        active_agents = HumeAgent.objects.filter(status='active').count()
        
        # Sentiment distribution
        sentiment_dist = CallAnalytics.objects.filter(
            created_at__gte=start_date
        ).values('overall_sentiment').annotate(count=Count('id'))
        
        # Average call duration
        avg_duration = TwilioCall.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).aggregate(avg=Avg('duration'))['avg'] or 0
        
        return Response({
            'period_days': days,
            'total_calls': total_calls,
            'calls_by_status': list(calls_by_status),
            'total_duration': total_duration,
            'avg_duration': round(avg_duration, 2),
            'active_agents': active_agents,
            'sentiment_distribution': list(sentiment_dist)
        })
    
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_calls(request):
    """
    Get recent calls with basic info
    """
    try:
        limit = int(request.query_params.get('limit', 10))
        
        calls = TwilioCall.objects.select_related('agent').order_by('-created_at')[:limit]
        serializer = TwilioCallListSerializer(calls, many=True)
        
        return Response(serializer.data)
    
    except Exception as e:
        logger.error(f"Recent calls error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
