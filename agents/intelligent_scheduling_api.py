from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .intelligent_response_scheduler import intelligent_scheduler
from .ai_agent_models import AIAgent, CallSession
from .auto_campaign_models import AutoCallCampaign

logger = logging.getLogger(__name__)


class IntelligentSchedulingRulesAPIView(APIView):
    """API for managing intelligent scheduling rules based on customer responses"""
    
    def get(self, request):
        """Get current intelligent scheduling rules"""
        try:
            rules = intelligent_scheduler.get_scheduling_rules()
            
            # Add some statistics about rule usage
            rule_stats = {}
            for outcome, rule in rules.items():
                # Get count of calls with this outcome in last 30 days
                recent_calls = CallSession.objects.filter(
                    outcome=outcome,
                    completed_at__gte=timezone.now() - timedelta(days=30)
                ).count()
                
                rule_stats[outcome] = {
                    'rule': rule,
                    'usage_last_30_days': recent_calls
                }
            
            return Response({
                'success': True,
                'intelligent_scheduling_rules': rule_stats,
                'total_outcomes': len(rules),
                'system_info': {
                    'description': 'Intelligent auto-scheduler automatically schedules next calls based on customer responses',
                    'urdu_description': 'Customer ke response ke base par automatically next calls schedule karta hai',
                    'outcomes_supported': list(rules.keys())
                }
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to get scheduling rules: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update intelligent scheduling rules"""
        try:
            data = request.data
            outcome = data.get('outcome')
            new_rule = data.get('rule')
            
            if not outcome or not new_rule:
                return Response({
                    'error': 'outcome and rule are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the rule
            success = intelligent_scheduler.update_scheduling_rule(outcome, new_rule)
            
            if success:
                return Response({
                    'success': True,
                    'outcome': outcome,
                    'updated_rule': new_rule,
                    'message': f'Scheduling rule for "{outcome}" updated successfully'
                })
            else:
                return Response({
                    'error': f'Invalid outcome: {outcome}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'Failed to update rule: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CallOutcomeStatsAPIView(APIView):
    """API for call outcome statistics and scheduling insights"""
    
    def get(self, request):
        """Get call outcome statistics"""
        try:
            ai_agent = AIAgent.objects.get(user=request.user)
            
            # Get call outcomes from last 30 days
            recent_calls = CallSession.objects.filter(
                ai_agent=ai_agent,
                completed_at__gte=timezone.now() - timedelta(days=30)
            )
            
            # Count by outcome
            outcome_counts = {}
            total_calls = recent_calls.count()
            
            for call in recent_calls:
                outcome = call.outcome
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
            
            # Calculate percentages
            outcome_percentages = {}
            for outcome, count in outcome_counts.items():
                percentage = (count / total_calls * 100) if total_calls > 0 else 0
                outcome_percentages[outcome] = {
                    'count': count,
                    'percentage': round(percentage, 1)
                }
            
            # Get scheduling effectiveness
            scheduled_follow_ups = 0
            completed_follow_ups = 0
            
            # This would need more complex logic to track follow-up effectiveness
            # For now, we'll provide basic stats
            
            return Response({
                'success': True,
                'agent_id': str(ai_agent.id),
                'agent_name': ai_agent.name,
                'period': 'Last 30 days',
                'total_calls': total_calls,
                'outcome_statistics': outcome_percentages,
                'most_common_outcome': max(outcome_counts.items(), key=lambda x: x[1])[0] if outcome_counts else None,
                'intelligent_scheduling_stats': {
                    'scheduled_follow_ups': scheduled_follow_ups,
                    'completed_follow_ups': completed_follow_ups,
                    'effectiveness': 'Data collection in progress'
                },
                'recommendations': self._generate_recommendations(outcome_percentages)
            })
            
        except AIAgent.DoesNotExist:
            return Response({
                'error': 'No AI agent found for this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to get statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_recommendations(self, outcome_percentages):
        """Generate intelligent recommendations based on call outcomes"""
        recommendations = []
        
        # Check for high not_interested rate
        not_interested_rate = outcome_percentages.get('not_interested', {}).get('percentage', 0)
        if not_interested_rate > 50:
            recommendations.append({
                'type': 'script_improvement',
                'message': 'High not_interested rate detected. Consider improving your script or targeting.',
                'urdu': 'زیادہ "دلچسپی نہیں" responses آ رہے ہیں۔ Script یا targeting بہتر کریں۔'
            })
        
        # Check for high no_answer rate
        no_answer_rate = outcome_percentages.get('no_answer', {}).get('percentage', 0)
        if no_answer_rate > 30:
            recommendations.append({
                'type': 'timing_optimization',
                'message': 'High no_answer rate. Consider adjusting call timing or frequency.',
                'urdu': 'کافی calls کا جواب نہیں مل رہا۔ Call کا time یا frequency adjust کریں۔'
            })
        
        # Check for good interested rate
        interested_rate = outcome_percentages.get('interested', {}).get('percentage', 0)
        if interested_rate > 20:
            recommendations.append({
                'type': 'follow_up_optimization',
                'message': 'Good interested rate! Optimize follow-up timing for better conversions.',
                'urdu': 'اچھا interest rate ہے! Follow-up timing optimize کریں۔'
            })
        
        return recommendations


class TestIntelligentSchedulingAPIView(APIView):
    """API for testing intelligent scheduling system"""
    
    def post(self, request):
        """Test intelligent scheduling with sample data"""
        try:
            data = request.data
            test_outcome = data.get('test_outcome', 'interested')
            
            # Get current rules
            rules = intelligent_scheduler.get_scheduling_rules()
            
            if test_outcome not in rules:
                return Response({
                    'error': f'Invalid test outcome: {test_outcome}',
                    'valid_outcomes': list(rules.keys())
                }, status=status.HTTP_400_BAD_REQUEST)
            
            rule = rules[test_outcome]
            
            # Calculate when next call would be scheduled
            next_call_time = timezone.now() + timedelta(minutes=rule['follow_up_delay'])
            
            return Response({
                'success': True,
                'test_outcome': test_outcome,
                'rule_applied': rule,
                'simulated_scheduling': {
                    'next_call_scheduled_at': next_call_time,
                    'delay_minutes': rule['follow_up_delay'],
                    'priority_assigned': rule['priority'],
                    'call_type': rule['call_type'],
                    'action': rule['next_action']
                },
                'explanation': {
                    'english': f"If customer responds '{test_outcome}', next call will be scheduled in {rule['follow_up_delay']} minutes with priority {rule['priority']}",
                    'urdu': f"اگر customer '{test_outcome}' response دے تو اگلی call {rule['follow_up_delay']} منٹ بعد priority {rule['priority']} کے ساتھ schedule ہوگی"
                }
            })
            
        except Exception as e:
            return Response({
                'error': f'Test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)