"""
📊 CLARIFIES Analytics API Views

New APIs for conversation analytics:
1. /api/analytics/conversation-metrics/ - Overall metrics
2. /api/analytics/objection-types/ - Objection breakdown
3. /api/analytics/clarifies-flow/ - Flow analysis
4. /api/analytics/win-loss-rate/ - Outcome metrics
5. /api/analytics/tone-trends/ - Sentiment over time
6. /api/call/<call_id>/explainability/ - Detailed call analysis
7. /api/analytics/risk-flags/ - Flagged content audit
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

from HumeAiTwilio.models import (
    TwilioCall,
    CallObjection,
    CLARIFIESStep,
    ConversationAnalytics,
    RiskFlag,
    ConversationLog
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_metrics(request):
    """
    GET /api/analytics/conversation-metrics/
    
    Query params:
    - date_from: Start date (YYYY-MM-DD)
    - date_to: End date (YYYY-MM-DD)
    - agent_id: Filter by agent
    - campaign: Filter by campaign
    
    Returns:
    - Total calls analyzed
    - Average objections per call
    - Resolution rate
    - Win/loss/follow-up breakdown
    - Average conversation quality score
    """
    try:
        user = request.user
        
        # Date filters
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        agent_id = request.GET.get('agent_id')
        
        # Default to last 30 days
        if not date_from:
            date_from = (timezone.now() - timedelta(days=30)).date()
        if not date_to:
            date_to = timezone.now().date()
        
        # Base query
        analytics_query = ConversationAnalytics.objects.filter(
            call__user=user,
            analyzed_at__date__gte=date_from,
            analyzed_at__date__lte=date_to
        )
        
        if agent_id:
            analytics_query = analytics_query.filter(call__agent_id=agent_id)
        
        # Aggregate metrics
        total_calls = analytics_query.count()
        
        objection_stats = analytics_query.aggregate(
            avg_objections=Avg('total_objections'),
            avg_resolved=Avg('objections_resolved'),
            avg_escalated=Avg('objections_escalated')
        )
        
        # Calculate resolution rate
        total_objections = sum([a.total_objections for a in analytics_query])
        total_resolved = sum([a.objections_resolved for a in analytics_query])
        resolution_rate = (total_resolved / total_objections * 100) if total_objections > 0 else 0
        
        # Outcome breakdown
        outcome_breakdown = analytics_query.values('outcome').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Quality metrics
        quality_stats = analytics_query.aggregate(
            avg_sentiment=Avg('avg_sentiment'),
            avg_win_probability=Avg('win_probability')
        )
        
        # Sentiment trend distribution
        sentiment_trends = analytics_query.values('sentiment_trend').annotate(
            count=Count('id')
        )
        
        return Response({
            'success': True,
            'date_range': {
                'from': str(date_from),
                'to': str(date_to)
            },
            'metrics': {
                'total_calls': total_calls,
                'avg_objections_per_call': round(objection_stats['avg_objections'] or 0, 2),
                'avg_resolved_per_call': round(objection_stats['avg_resolved'] or 0, 2),
                'avg_escalated_per_call': round(objection_stats['avg_escalated'] or 0, 2),
                'overall_resolution_rate': round(resolution_rate, 2),
                'avg_sentiment_score': round(quality_stats['avg_sentiment'] or 0, 2),
                'avg_win_probability': round(quality_stats['avg_win_probability'] or 0, 2),
            },
            'outcome_breakdown': list(outcome_breakdown),
            'sentiment_trends': list(sentiment_trends)
        })
        
    except Exception as e:
        logger.error(f"Error fetching conversation metrics: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def objection_types(request):
    """
    GET /api/analytics/objection-types/
    
    Returns breakdown of objection types with resolution stats
    """
    try:
        user = request.user
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        agent_id = request.GET.get('agent_id')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=30)).date()
        if not date_to:
            date_to = timezone.now().date()
        
        # Base query
        objections_query = CallObjection.objects.filter(
            call__user=user,
            detected_at__date__gte=date_from,
            detected_at__date__lte=date_to
        )
        
        if agent_id:
            objections_query = objections_query.filter(call__agent_id=agent_id)
        
        # Objection type breakdown
        objection_stats = objections_query.values('objection_type').annotate(
            total=Count('id'),
            resolved=Count('id', filter=Q(resolution_status='resolved')),
            escalated=Count('id', filter=Q(resolution_status='escalated')),
            pending=Count('id', filter=Q(resolution_status='pending')),
            avg_confidence=Avg('confidence_score')
        ).order_by('-total')
        
        # Add resolution rate for each type
        results = []
        for obj_stat in objection_stats:
            resolution_rate = (obj_stat['resolved'] / obj_stat['total'] * 100) if obj_stat['total'] > 0 else 0
            results.append({
                'objection_type': obj_stat['objection_type'],
                'total_count': obj_stat['total'],
                'resolved_count': obj_stat['resolved'],
                'escalated_count': obj_stat['escalated'],
                'pending_count': obj_stat['pending'],
                'resolution_rate': round(resolution_rate, 2),
                'avg_confidence': round(obj_stat['avg_confidence'] or 0, 2)
            })
        
        return Response(results)  # Return array directly for charts
        
    except Exception as e:
        logger.error(f"Error fetching objection types: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clarifies_flow_analysis(request):
    """
    GET /api/analytics/clarifies-flow/
    
    Returns:
    - Most common CLARIFIES step sequences
    - Average steps per call
    - Effectiveness scores by step
    """
    try:
        user = request.user
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=30)).date()
        if not date_to:
            date_to = timezone.now().date()
        
        # Get all analytics with CLARIFIES data
        analytics = ConversationAnalytics.objects.filter(
            call__user=user,
            analyzed_at__date__gte=date_from,
            analyzed_at__date__lte=date_to
        )
        
        # Step usage statistics
        steps_query = CLARIFIESStep.objects.filter(
            call__user=user,
            timestamp__date__gte=date_from,
            timestamp__date__lte=date_to
        )
        
        step_stats = steps_query.values('step_type').annotate(
            usage_count=Count('id'),
            avg_effectiveness=Avg('effectiveness_score'),
            avg_duration=Avg('duration_seconds')
        ).order_by('-usage_count')
        
        # Average steps per call
        avg_steps_per_call = analytics.aggregate(
            avg_total_steps=Avg('total_steps')
        )['avg_total_steps'] or 0
        
        # Most common step sequences
        step_sequences = {}
        for analytic in analytics:
            sequence = ' → '.join(analytic.clarifies_steps_used[:5])  # First 5 steps
            if sequence:
                step_sequences[sequence] = step_sequences.get(sequence, 0) + 1
        
        # Sort by frequency
        common_sequences = sorted(
            [{'sequence': k, 'count': v} for k, v in step_sequences.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]  # Top 10
        
        # Return step_statistics array directly for frontend charts
        results = []
        for stat in step_stats:
            results.append({
                'step': stat['step_type'],
                'count': stat['usage_count'],
                'avg_effectiveness': round(stat['avg_effectiveness'] or 0, 2),
                'common_next_steps': []  # Can be populated later
            })
        
        return Response(results)  # Return array directly
        
    except Exception as e:
        logger.error(f"Error analyzing CLARIFIES flow: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def win_loss_rate(request):
    """
    GET /api/analytics/win-loss-rate/
    
    Returns win/loss/follow-up rates with trends
    """
    try:
        user = request.user
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        agent_id = request.GET.get('agent_id')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=30)).date()
        if not date_to:
            date_to = timezone.now().date()
        
        analytics_query = ConversationAnalytics.objects.filter(
            call__user=user,
            analyzed_at__date__gte=date_from,
            analyzed_at__date__lte=date_to
        )
        
        if agent_id:
            analytics_query = analytics_query.filter(call__agent_id=agent_id)
        
        # Outcome counts
        total_calls = analytics_query.count()
        outcome_counts = analytics_query.values('outcome').annotate(count=Count('id'))
        
        # Calculate rates
        outcomes = {item['outcome']: item['count'] for item in outcome_counts}
        
        won_count = outcomes.get('WIN', 0)
        lost_count = outcomes.get('LOSS', 0)
        follow_up_count = outcomes.get('FOLLOW_UP', 0)
        
        # Format as array for frontend charts
        outcomes_array = [
            {
                'outcome': 'Won',
                'count': won_count,
                'percentage': round((won_count / total_calls * 100) if total_calls > 0 else 0, 2)
            },
            {
                'outcome': 'Lost',
                'count': lost_count,
                'percentage': round((lost_count / total_calls * 100) if total_calls > 0 else 0, 2)
            },
            {
                'outcome': 'Follow Up',
                'count': follow_up_count,
                'percentage': round((follow_up_count / total_calls * 100) if total_calls > 0 else 0, 2)
            }
        ]
        
        return Response(outcomes_array)  # Return array directly for charts
        
    except Exception as e:
        logger.error(f"Error calculating win/loss rate: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tone_trends(request):
    """
    GET /api/analytics/tone-trends/
    
    Returns sentiment and emotion trends over time
    """
    try:
        user = request.user
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=30)).date()
        if not date_to:
            date_to = timezone.now().date()
        
        analytics_query = ConversationAnalytics.objects.filter(
            call__user=user,
            analyzed_at__date__gte=date_from,
            analyzed_at__date__lte=date_to
        )
        
        # Daily sentiment averages
        daily_sentiment = analytics_query.extra(
            select={'day': 'DATE(analyzed_at)'}
        ).values('day').annotate(
            avg_sentiment=Avg('avg_sentiment'),
            call_count=Count('id')
        ).order_by('day')
        
        # Dominant emotions breakdown
        emotions = {}
        for analytic in analytics_query:
            emotion = analytic.dominant_customer_emotion
            if emotion:
                emotions[emotion] = emotions.get(emotion, 0) + 1
        
        emotion_breakdown = sorted(
            [{'emotion': k, 'count': v} for k, v in emotions.items()],
            key=lambda x: x['count'],
            reverse=True
        )
        
        # Format for frontend LineChart
        results = []
        for day_data in daily_sentiment:
            results.append({
                'date': str(day_data['day']),
                'avg_sentiment': round(day_data['avg_sentiment'] or 0, 2),
                'positive_count': day_data['call_count'] if day_data['avg_sentiment'] > 0 else 0,
                'negative_count': day_data['call_count'] if day_data['avg_sentiment'] < 0 else 0,
                'neutral_count': day_data['call_count'] if day_data['avg_sentiment'] == 0 else 0,
                'top_emotions': {}  # Can add emotion breakdown per day later
            })
        
        return Response(results)  # Return array directly
        
    except Exception as e:
        logger.error(f"Error analyzing tone trends: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def call_explainability(request, call_id):
    """
    GET /api/call/<call_id>/explainability/
    
    Returns complete explainable AI analysis for a specific call:
    - Full transcript with timestamps
    - All objections detected with reasoning
    - CLARIFIES step-by-step logic
    - Decision points and alternatives
    - Sentiment/emotion evolution
    """
    try:
        user = request.user
        
        # Get call
        call = TwilioCall.objects.filter(
            call_sid=call_id,
            user=user
        ).first()
        
        if not call:
            return Response({
                'success': False,
                'error': 'Call not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get transcript
        conversation_logs = ConversationLog.objects.filter(
            call=call
        ).order_by('timestamp')
        
        transcript = [{
            'timestamp': log.timestamp.isoformat(),
            'speaker': log.role,
            'message': log.message,
            'emotions': log.emotions or {}
        } for log in conversation_logs]
        
        # Get objections
        objections = CallObjection.objects.filter(call=call).order_by('detected_at')
        objections_data = [{
            'id': str(obj.id),
            'type': obj.objection_type,
            'text': obj.objection_text,
            'detected_at': obj.detected_at.isoformat(),
            'clarifies_step_used': obj.clarifies_step,
            'agent_response': obj.agent_response,
            'resolution_status': obj.resolution_status,
            'confidence': obj.confidence_score,
            'sentiment_before': obj.sentiment_before,
            'sentiment_after': obj.sentiment_after
        } for obj in objections]
        
        # Get CLARIFIES steps
        clarifies_steps = CLARIFIESStep.objects.filter(call=call).order_by('step_number')
        steps_data = [{
            'step_number': step.step_number,
            'step_type': step.step_type,
            'step_name': step.get_step_type_display(),
            'customer_message': step.customer_message,
            'agent_message': step.agent_message,
            'reasoning': step.reasoning,
            'decision_factors': step.decision_factors,
            'alternative_paths': step.alternative_paths,
            'effectiveness_score': step.effectiveness_score,
            'timestamp': step.timestamp.isoformat()
        } for step in clarifies_steps]
        
        # Get analytics
        analytics = ConversationAnalytics.objects.filter(call=call).first()
        analytics_data = None
        if analytics:
            analytics_data = {
                'outcome': analytics.outcome,
                'win_probability': analytics.win_probability,
                'total_objections': analytics.total_objections,
                'objections_resolved': analytics.objections_resolved,
                'resolution_rate': analytics.resolution_rate,
                'clarifies_flow': analytics.clarifies_steps_used,
                'avg_sentiment': analytics.avg_sentiment,
                'sentiment_trend': analytics.sentiment_trend,
                'dominant_emotion': analytics.dominant_customer_emotion,
                'key_decision_moments': analytics.key_decision_moments
            }
        
        return Response({
            'success': True,
            'call': {
                'call_sid': call.call_sid,
                'status': call.status,
                'duration': call.duration,
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None,
                'agent': call.agent.name if call.agent else None
            },
            'transcript': transcript,
            'objections': objections_data,
            'clarifies_steps': steps_data,
            'analytics': analytics_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching call explainability: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def risk_flags_audit(request):
    """
    GET /api/analytics/risk-flags/
    
    Returns all flagged content for admin review
    Query params:
    - status: pending/approved/rejected/auto_blocked
    - risk_level: low/medium/high/critical
    - date_from, date_to
    """
    try:
        user = request.user
        
        # Only allow admins to view risk flags
        if not user.is_staff:
            return Response({
                'success': False,
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        status_filter = request.GET.get('status')
        risk_level = request.GET.get('risk_level')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        flags_query = RiskFlag.objects.all()
        
        if status_filter:
            flags_query = flags_query.filter(status=status_filter)
        if risk_level:
            flags_query = flags_query.filter(risk_level=risk_level)
        if date_from:
            flags_query = flags_query.filter(detected_at__date__gte=date_from)
        if date_to:
            flags_query = flags_query.filter(detected_at__date__lte=date_to)
        
        flags_query = flags_query.order_by('-detected_at')[:100]  # Limit to 100
        
        flags_data = [{
            'id': str(flag.id),
            'call_sid': flag.call.call_sid,
            'flagged_content': flag.flagged_content,
            'flag_reason': flag.flag_reason,
            'risk_level': flag.risk_level,
            'risk_category': flag.risk_category,
            'was_blocked': flag.was_blocked,
            'replacement_sent': flag.replacement_sent,
            'status': flag.status,
            'detected_at': flag.detected_at.isoformat(),
            'reviewed_by': flag.reviewed_by.username if flag.reviewed_by else None,
            'reviewed_at': flag.reviewed_at.isoformat() if flag.reviewed_at else None
        } for flag in flags_query]
        
        # Summary statistics
        summary = {
            'total_flags': RiskFlag.objects.count(),
            'pending_review': RiskFlag.objects.filter(status='pending').count(),
            'auto_blocked': RiskFlag.objects.filter(status='auto_blocked').count(),
            'by_risk_level': list(
                RiskFlag.objects.values('risk_level').annotate(count=Count('id'))
            )
        }
        
        return Response({
            'success': True,
            'flags': flags_data,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error fetching risk flags: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




