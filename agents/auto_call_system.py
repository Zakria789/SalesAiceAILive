from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import logging

from .auto_campaign_models import AutoCallCampaign, AutoCampaignContact
from .ai_agent_models import AIAgent, CustomerProfile, CallSession
from .intelligent_response_scheduler import intelligent_scheduler

logger = logging.getLogger(__name__)


class AutoCallCampaignAPIView(APIView):
    """API View for managing auto call campaigns"""
    
    def _initiate_call(self, contact):
        """
        Initiate a call for the given contact
        Auto-schedules next calls when current call starts
        """
        try:
            # Placeholder for actual call initiation
            logger.info(f"🚀 Initiating call to {contact.customer_profile.phone_number}")
            
            # Update contact status
            contact.call_started_at = timezone.now()
            contact.status = 'calling'
            contact.save()
            
            # 🔄 AUTO-SCHEDULE NEXT CALLS (یہاں magic ہے!)
            campaign = contact.campaign
            if campaign.status == 'active':
                scheduled_count = self._schedule_next_calls(campaign)
                logger.info(f"📅 Auto-scheduled {scheduled_count} next calls for campaign {campaign.name}")
            
            # TODO: Add actual Twilio integration here
            # from .twilio_service import TwilioCallService
            # twilio_service = TwilioCallService()
            # call_result = twilio_service.initiate_call(
            #     to=contact.customer_profile.phone_number,
            #     agent_config={...}
            # )
            
            return {
                'success': True,
                'call_id': f'mock_call_{contact.id}',
                'message': f'Call initiated to {contact.customer_profile.phone_number}',
                'auto_scheduled': True,
                'intelligent_scheduling_ready': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to initiate call for contact {contact.id}: {str(e)}")
            contact.status = 'failed'
            contact.failure_reason = str(e)
            contact.save()
            
            return {
                'success': False,
                'error': str(e)
            }

    def complete_call_with_outcome(self, request):
        """
        Complete call and trigger intelligent scheduling based on customer response
        Customer response ke base par automatically next calls schedule karta hai
        """
        try:
            data = request.data
            contact_id = data.get('contact_id')
            call_outcome = data.get('call_outcome')  # interested, not_interested, callback_requested, etc.
            customer_response = data.get('customer_response', '')
            call_duration = data.get('call_duration', 0)
            agent_notes = data.get('agent_notes', '')
            
            if not contact_id or not call_outcome:
                return Response({
                    'error': 'contact_id and call_outcome are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the contact and campaign
            contact = get_object_or_404(AutoCampaignContact, id=contact_id)
            campaign = contact.campaign
            customer = contact.customer_profile
            agent = campaign.ai_agent
            
            # Update contact status
            contact.status = 'completed'
            contact.call_completed_at = timezone.now()
            contact.call_outcome = call_outcome
            contact.save()
            
            # Create or update CallSession
            call_session, created = CallSession.objects.get_or_create(
                ai_agent=agent,
                customer_profile=customer,
                phone_number=customer.phone_number,
                defaults={
                    'call_type': 'outbound',
                    'outcome': call_outcome,
                    'initiated_at': contact.call_started_at or timezone.now(),
                    'completed_at': timezone.now(),
                    'agent_notes': agent_notes,
                    'conversation_notes': {
                        'customer_response': customer_response,
                        'call_duration': call_duration,
                        'campaign_id': str(campaign.id),
                        'campaign_name': campaign.name
                    }
                }
            )
            
            if not created:
                call_session.outcome = call_outcome
                call_session.completed_at = timezone.now()
                call_session.agent_notes = agent_notes
                call_session.save()
            
            # 🧠 INTELLIGENT SCHEDULING MAGIC! 
            # Customer response ke base par automatically next calls schedule karta hai
            scheduling_result = intelligent_scheduler.process_call_outcome_and_schedule(
                call_session=call_session,
                campaign=campaign
            )
            
            logger.info(f"🎯 Call completed for {customer.phone_number}: {call_outcome}")
            if scheduling_result.get('next_call_scheduled'):
                logger.info(f"🚀 Next call auto-scheduled based on customer response!")
            
            return Response({
                'success': True,
                'call_completed': True,
                'contact_id': str(contact.id),
                'call_outcome': call_outcome,
                'customer_phone': customer.phone_number,
                'intelligent_scheduling': scheduling_result,
                'next_action': scheduling_result.get('rule_applied'),
                'customer_interest_updated': scheduling_result.get('customer_updated'),
                'message': f'Call completed and intelligent scheduling applied based on customer response: {call_outcome}'
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to complete call and schedule: {str(e)}")
            return Response({
                'error': f'Failed to complete call: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get campaign status"""
        return Response({
            'status': 'AutoCallCampaignAPIView is working',
            'timestamp': timezone.now()
        })
    
    def post(self, request):
        """Create new auto-call campaign"""
        try:
            data = request.data
            
            # Get AI agent for the user
            try:
                ai_agent = AIAgent.objects.get(user=request.user)
            except AIAgent.DoesNotExist:
                return Response({
                    'error': 'No AI agent found for this user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create campaign
            campaign = AutoCallCampaign.objects.create(
                ai_agent=ai_agent,
                name=data.get('campaign_name', f'Campaign {timezone.now().strftime("%Y%m%d_%H%M")}'),
                campaign_type=data.get('campaign_type', 'sales'),
                calls_per_hour=data.get('calls_per_hour', 5),
                working_hours_start=data.get('working_hours_start', '09:00'),
                working_hours_end=data.get('working_hours_end', '17:00'),
                target_customers=data.get('target_customers', 10),
                status='active',
                started_at=timezone.now()
            )
            
            # Add customers to campaign
            customer_filters = data.get('customer_filters', {})
            interest_levels = customer_filters.get('interest_levels', ['warm', 'hot'])
            max_customers = customer_filters.get('max_customers', 10)
            
            customers = CustomerProfile.objects.filter(
                ai_agent=ai_agent,
                is_do_not_call=False,
                interest_level__in=interest_levels
            )[:max_customers]
            
            # Create campaign contacts
            contacts_created = 0
            for customer in customers:
                AutoCampaignContact.objects.create(
                    campaign=campaign,
                    customer_profile=customer,
                    status='pending',
                    priority=3 if customer.interest_level == 'hot' else 2,
                    scheduled_datetime=timezone.now()
                )
                contacts_created += 1
            
            # Start immediate calls if requested
            immediate_calls = data.get('immediate_calls', 0)
            if immediate_calls > 0:
                self._start_immediate_calls(campaign, immediate_calls)
            
            return Response({
                'success': True,
                'campaign_id': str(campaign.id),
                'campaign_name': campaign.name,
                'status': campaign.status,
                'contacts_added': contacts_created,
                'calls_per_hour': campaign.calls_per_hour,
                'working_hours': f"{campaign.working_hours_start} - {campaign.working_hours_end}",
                'message': f'Campaign "{campaign.name}" created successfully with {contacts_created} contacts'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {str(e)}")
            return Response({
                'error': f'Failed to create campaign: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, campaign_id=None):
        """Update campaign settings"""
        try:
            if not campaign_id:
                return Response({
                    'error': 'Campaign ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ai_agent = AIAgent.objects.get(user=request.user)
            campaign = get_object_or_404(AutoCallCampaign, id=campaign_id, ai_agent=ai_agent)
            
            data = request.data
            
            # Update campaign settings
            if 'status' in data:
                campaign.status = data['status']
            if 'calls_per_hour' in data:
                campaign.calls_per_hour = data['calls_per_hour']
            if 'working_hours_start' in data:
                campaign.working_hours_start = data['working_hours_start']
            if 'working_hours_end' in data:
                campaign.working_hours_end = data['working_hours_end']
            
            campaign.save()
            
            return Response({
                'success': True,
                'campaign_id': str(campaign.id),
                'status': campaign.status,
                'message': 'Campaign updated successfully'
            })
            
        except AIAgent.DoesNotExist:
            return Response({
                'error': 'No AI agent found for this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to update campaign: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, campaign_id=None):
        """Stop/delete campaign"""
        try:
            ai_agent = AIAgent.objects.get(user=request.user)
            campaign = get_object_or_404(AutoCallCampaign, id=campaign_id, ai_agent=ai_agent)
            
            # Mark as cancelled instead of deleting
            campaign.status = 'cancelled'
            campaign.completed_at = timezone.now()
            campaign.save()
            
            return Response({
                'success': True,
                'message': f'Campaign "{campaign.name}" stopped successfully'
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to stop campaign: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _start_immediate_calls(self, campaign, count):
        """Start immediate calls for campaign"""
        pending_contacts = campaign.contacts.filter(status='pending')[:count]
        
        for contact in pending_contacts:
            result = self._initiate_call(contact)
            logger.info(f"Immediate call result: {result}")
    
    def _schedule_next_calls(self, campaign):
        """Schedule next batch of calls based on calls_per_hour setting"""
        try:
            # Calculate next call time based on calls_per_hour
            minutes_between_calls = 60 / campaign.calls_per_hour
            next_call_time = timezone.now() + timedelta(minutes=minutes_between_calls)
            
            # Get pending contacts
            pending_contacts = campaign.contacts.filter(
                status='pending'
            ).order_by('-priority', 'scheduled_datetime')[:3]  # Next 3 calls
            
            calls_scheduled = 0
            for contact in pending_contacts:
                # Update scheduled time
                contact.scheduled_datetime = next_call_time + timedelta(minutes=calls_scheduled * 2)
                contact.save()
                calls_scheduled += 1
            
            logger.info(f"Scheduled {calls_scheduled} calls for campaign {campaign.name}")
            return calls_scheduled
            
        except Exception as e:
            logger.error(f"Failed to schedule next calls: {str(e)}")
            return 0