from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import logging

from .auto_campaign_models import AutoCallCampaign, AutoCampaignContact
from .ai_agent_models import AIAgent, CustomerProfile

logger = logging.getLogger(__name__)


class CampaignScheduleAPIView(APIView):
    """API for managing campaign schedules and auto-scheduling"""
    
    def get(self, request, campaign_id=None):
        """Get campaign schedule status or list all campaigns"""
        try:
            ai_agent = AIAgent.objects.get(user=request.user)
            
            if campaign_id:
                # Get specific campaign details
                campaign = get_object_or_404(AutoCallCampaign, id=campaign_id, ai_agent=ai_agent)
                
                # Get campaign statistics
                total_contacts = campaign.contacts.count()
                pending_calls = campaign.contacts.filter(status='pending').count()
                completed_calls = campaign.contacts.filter(status='completed').count()
                active_calls = campaign.contacts.filter(status='calling').count()
                failed_calls = campaign.contacts.filter(status='failed').count()
                
                # Get next scheduled calls
                next_calls = campaign.contacts.filter(
                    status='pending'
                ).order_by('scheduled_datetime')[:5]
                
                return Response({
                    'campaign': {
                        'id': str(campaign.id),
                        'name': campaign.name,
                        'status': campaign.status,
                        'campaign_type': campaign.campaign_type,
                        'calls_per_hour': campaign.calls_per_hour,
                        'working_hours': f"{campaign.working_hours_start} - {campaign.working_hours_end}",
                        'created_at': campaign.created_at,
                        'started_at': campaign.started_at,
                    },
                    'statistics': {
                        'total_contacts': total_contacts,
                        'pending_calls': pending_calls,
                        'completed_calls': completed_calls,
                        'active_calls': active_calls,
                        'failed_calls': failed_calls,
                        'completion_percentage': round((completed_calls / total_contacts * 100) if total_contacts > 0 else 0, 1)
                    },
                    'next_scheduled_calls': [
                        {
                            'contact_id': str(call.id),
                            'customer_name': call.customer_profile.name,
                            'phone_number': call.customer_profile.phone_number,
                            'scheduled_time': call.scheduled_datetime,
                            'priority': call.priority
                        } for call in next_calls
                    ],
                    'auto_scheduling_active': campaign.status == 'active'
                })
            
            else:
                # List all campaigns
                campaigns = AutoCallCampaign.objects.filter(ai_agent=ai_agent).order_by('-created_at')
                
                campaign_list = []
                for campaign in campaigns:
                    total_contacts = campaign.contacts.count()
                    completed_calls = campaign.contacts.filter(status='completed').count()
                    
                    campaign_list.append({
                        'id': str(campaign.id),
                        'name': campaign.name,
                        'status': campaign.status,
                        'calls_per_hour': campaign.calls_per_hour,
                        'total_contacts': total_contacts,
                        'completed_calls': completed_calls,
                        'progress': round((completed_calls / total_contacts * 100) if total_contacts > 0 else 0, 1),
                        'created_at': campaign.created_at,
                        'is_auto_scheduling': campaign.status == 'active'
                    })
                
                return Response({
                    'campaigns': campaign_list,
                    'total_campaigns': len(campaign_list),
                    'active_campaigns': len([c for c in campaign_list if c['status'] == 'active'])
                })
                
        except AIAgent.DoesNotExist:
            return Response({
                'error': 'No AI agent found for this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to get campaign data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Manual schedule control - force schedule next calls or pause/resume"""
        try:
            ai_agent = AIAgent.objects.get(user=request.user)
            data = request.data
            action = data.get('action')
            campaign_id = data.get('campaign_id')
            
            if not campaign_id:
                return Response({
                    'error': 'campaign_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            campaign = get_object_or_404(AutoCallCampaign, id=campaign_id, ai_agent=ai_agent)
            
            if action == 'schedule_now':
                # Force schedule next batch of calls immediately
                count = data.get('count', 3)
                pending_contacts = campaign.contacts.filter(status='pending')[:count]
                
                scheduled_calls = []
                for i, contact in enumerate(pending_contacts):
                    # Schedule calls with 2-minute intervals
                    schedule_time = timezone.now() + timedelta(minutes=i * 2)
                    contact.scheduled_datetime = schedule_time
                    contact.save()
                    
                    scheduled_calls.append({
                        'customer_name': contact.customer_profile.name,
                        'phone_number': contact.customer_profile.phone_number,
                        'scheduled_time': schedule_time
                    })
                
                return Response({
                    'success': True,
                    'action': 'schedule_now',
                    'scheduled_calls': scheduled_calls,
                    'message': f'Scheduled {len(scheduled_calls)} calls for immediate execution'
                })
            
            elif action == 'pause_scheduling':
                # Pause auto-scheduling
                campaign.status = 'paused'
                campaign.save()
                
                return Response({
                    'success': True,
                    'action': 'pause_scheduling',
                    'campaign_status': 'paused',
                    'message': f'Auto-scheduling paused for campaign "{campaign.name}"'
                })
            
            elif action == 'resume_scheduling':
                # Resume auto-scheduling
                campaign.status = 'active'
                campaign.save()
                
                return Response({
                    'success': True,
                    'action': 'resume_scheduling',
                    'campaign_status': 'active',
                    'message': f'Auto-scheduling resumed for campaign "{campaign.name}"'
                })
            
            elif action == 'adjust_speed':
                # Adjust calls per hour
                new_calls_per_hour = data.get('calls_per_hour')
                if new_calls_per_hour:
                    campaign.calls_per_hour = new_calls_per_hour
                    campaign.save()
                    
                    return Response({
                        'success': True,
                        'action': 'adjust_speed',
                        'new_calls_per_hour': new_calls_per_hour,
                        'message': f'Call rate adjusted to {new_calls_per_hour} calls per hour'
                    })
            
            else:
                return Response({
                    'error': 'Invalid action. Use: schedule_now, pause_scheduling, resume_scheduling, adjust_speed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'Failed to execute action: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RealTimeAutoScheduler(APIView):
    """Real-time auto-scheduling control"""
    
    def post(self, request):
        """Trigger auto-scheduling for all active campaigns"""
        try:
            ai_agent = AIAgent.objects.get(user=request.user)
            
            # Get all active campaigns
            active_campaigns = AutoCallCampaign.objects.filter(
                ai_agent=ai_agent,
                status='active'
            )
            
            scheduling_results = []
            
            for campaign in active_campaigns:
                # Check if it's within working hours
                current_time = timezone.now().time()
                start_time = datetime.strptime(campaign.working_hours_start, '%H:%M').time()
                end_time = datetime.strptime(campaign.working_hours_end, '%H:%M').time()
                
                if start_time <= current_time <= end_time:
                    # Calculate calls to schedule based on calls_per_hour
                    minutes_between_calls = 60 / campaign.calls_per_hour
                    
                    # Get pending contacts
                    pending_contacts = campaign.contacts.filter(
                        status='pending'
                    ).order_by('-priority', 'scheduled_datetime')[:2]
                    
                    scheduled_count = 0
                    for i, contact in enumerate(pending_contacts):
                        # Schedule with proper intervals
                        schedule_time = timezone.now() + timedelta(minutes=(i + 1) * minutes_between_calls)
                        contact.scheduled_datetime = schedule_time
                        contact.save()
                        scheduled_count += 1
                    
                    scheduling_results.append({
                        'campaign_name': campaign.name,
                        'campaign_id': str(campaign.id),
                        'scheduled_calls': scheduled_count,
                        'status': 'scheduled'
                    })
                else:
                    scheduling_results.append({
                        'campaign_name': campaign.name,
                        'campaign_id': str(campaign.id),
                        'scheduled_calls': 0,
                        'status': 'outside_working_hours'
                    })
            
            return Response({
                'success': True,
                'auto_scheduling_results': scheduling_results,
                'total_campaigns_processed': len(active_campaigns),
                'timestamp': timezone.now(),
                'message': 'Real-time auto-scheduling completed'
            })
            
        except AIAgent.DoesNotExist:
            return Response({
                'error': 'No AI agent found for this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Auto-scheduling failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)