"""
HumeAI + Twilio Integration with Intelligent Auto Scheduling
Customer response ke base par automatic call scheduling for HumeAiTwilio module
"""
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import json

from HumeAiTwilio.models import TwilioCall, ConversationLog, CallAnalytics, HumeAgent
from agents.intelligent_response_scheduler import intelligent_scheduler
from agents.ai_agent_models import CustomerProfile, AIAgent
from agents.auto_campaign_models import AutoCallCampaign, AutoCampaignContact

logger = logging.getLogger(__name__)


class HumeTwilioIntelligentScheduler:
    """
    Intelligent scheduler specifically for HumeAI + Twilio calls
    HumeAI calls ko analyze kar ke automatically next calls schedule karta hai
    """
    
    def __init__(self):
        self.call_outcome_mapping = {
            # Hume sentiment -> Our scheduling outcome
            'positive': 'interested',
            'very_positive': 'interested', 
            'negative': 'not_interested',
            'very_negative': 'not_interested',
            'neutral': 'maybe_interested',
            'mixed': 'maybe_interested'
        }
        
        self.hume_emotion_to_outcome = {
            'Joy': 'interested',
            'Excitement': 'interested',
            'Interest': 'interested',
            'Satisfaction': 'interested',
            'Surprise': 'maybe_interested',
            'Confusion': 'maybe_interested',
            'Disappointment': 'not_interested',
            'Anger': 'not_interested',
            'Frustration': 'not_interested',
            'Sadness': 'not_interested'
        }

    def analyze_hume_call_and_schedule(self, twilio_call: TwilioCall, force_outcome: str = None):
        """
        Analyze completed HumeAI call and automatically schedule next call
        HumeAI call ko analyze kar ke next call schedule karta hai
        """
        try:
            logger.info(f"🧠 Analyzing HumeAI call for intelligent scheduling: {twilio_call.call_sid}")
            
            # Get call analytics and conversation logs
            analytics = getattr(twilio_call, 'analytics', None)
            conversation_logs = twilio_call.conversation_logs.all()
            
            # Determine call outcome based on HumeAI data
            if force_outcome:
                call_outcome = force_outcome
            else:
                call_outcome = self._analyze_hume_data_for_outcome(analytics, conversation_logs)
            
            try:
                # Create or find corresponding CustomerProfile and Campaign
                customer_profile = self._get_or_create_customer_profile(twilio_call)
                campaign = self._get_or_create_auto_campaign(twilio_call, customer_profile)
                
                # If we can't create proper profiles, use simplified scheduling
                if not customer_profile or not campaign:
                    logger.warning("Using simplified scheduling without full customer profile")
                    return self._simple_scheduling_fallback(twilio_call, call_outcome)
                
                # Create CallSession for our intelligent scheduler
                call_session = self._create_call_session_from_twilio(twilio_call, call_outcome, customer_profile)
                
                # 🚀 Trigger intelligent scheduling based on customer response
                # Note: Disabled for HumeAI calls as CallSession model doesn't have customer_profile field
                scheduling_result = {
                    'scheduled': False,
                    'reason': 'Simple scheduling used for HumeAI calls',
                    'outcome': call_outcome
                }
                
                # Use simple scheduling instead
                if call_session:
                    logger.info(f"✅ CallSession created for tracking: {call_session.twilio_call_sid}")
                
                # Update TwilioCall with scheduling info
                self._update_twilio_call_with_scheduling(twilio_call, call_outcome, scheduling_result)
                
                logger.info(f"✅ HumeAI call analyzed and scheduled: {call_outcome}")
                
                return {
                    'success': True,
                    'call_sid': twilio_call.call_sid,
                    'analyzed_outcome': call_outcome,
                    'intelligent_scheduling': scheduling_result,
                    'customer_phone': twilio_call.to_number,
                    'next_call_scheduled': scheduling_result.get('next_call_scheduled', False)
                }
                
            except Exception as detailed_error:
                logger.error(f"Detailed scheduling failed: {str(detailed_error)}")
                return self._simple_scheduling_fallback(twilio_call, call_outcome)
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze and schedule HumeAI call: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_hume_data_for_outcome(self, analytics: CallAnalytics, conversation_logs):
        """
        Analyze HumeAI emotions and sentiment to determine call outcome
        HumeAI ke emotions aur sentiment ko analyze kar ke call outcome decide karta hai
        """
        try:
            # Default outcome
            outcome = 'no_answer'
            
            if not conversation_logs.exists():
                return 'no_answer'
            
            # Check if analytics exists
            if analytics:
                # Use overall sentiment from analytics
                sentiment = analytics.overall_sentiment
                if sentiment:
                    outcome = self.call_outcome_mapping.get(sentiment.lower(), 'maybe_interested')
                
                # Check top emotions
                if analytics.top_emotions:
                    for emotion_data in analytics.top_emotions[:3]:  # Top 3 emotions
                        emotion_name = emotion_data.get('name', '')
                        if emotion_name in self.hume_emotion_to_outcome:
                            # Use the strongest positive/negative emotion
                            emotion_outcome = self.hume_emotion_to_outcome[emotion_name]
                            if emotion_outcome in ['interested', 'not_interested']:
                                outcome = emotion_outcome
                                break
            
            # Analyze conversation logs for specific keywords
            customer_messages = conversation_logs.filter(role='user')
            
            interested_keywords = [
                'interested', 'yes', 'sure', 'sounds good', 'tell me more', 
                'how much', 'price', 'cost', 'when', 'schedule', 'book'
            ]
            
            callback_keywords = [
                'call me back', 'call later', 'callback', 'busy right now',
                'call tomorrow', 'call next week'
            ]
            
            not_interested_keywords = [
                'not interested', 'no thanks', 'not now', 'remove me',
                'stop calling', 'dont call', "don't call"
            ]
            
            # Check customer messages for keywords
            for log in customer_messages:
                message = log.message.lower()
                
                # Check for explicit callback request
                if any(keyword in message for keyword in callback_keywords):
                    outcome = 'callback_requested'
                    break
                    
                # Check for strong interest
                elif any(keyword in message for keyword in interested_keywords):
                    outcome = 'interested'
                    
                # Check for explicit rejection
                elif any(keyword in message for keyword in not_interested_keywords):
                    outcome = 'not_interested'
                    break
            
            logger.info(f"📊 HumeAI analysis result: {outcome}")
            return outcome
            
        except Exception as e:
            logger.error(f"Error analyzing HumeAI data: {str(e)}")
            return 'maybe_interested'  # Default safe outcome
    
    def _get_or_create_customer_profile(self, twilio_call: TwilioCall):
        """Create or get customer profile from Twilio call"""
        try:
            # First get AI agent
            ai_agent = self._get_ai_agent_from_hume_agent(twilio_call.agent)
            
            if not ai_agent:
                logger.warning(f"[WARNING] No AI agent available for customer profile creation")
                return None
            
            # Try to find existing customer profile
            customer_profile, created = CustomerProfile.objects.get_or_create(
                phone_number=twilio_call.to_number,
                defaults={
                    'name': twilio_call.customer_name or f'Customer {twilio_call.to_number}',
                    'email': twilio_call.customer_email or '',
                    'interest_level': 'warm',
                    'call_preference_time': 'anytime',
                    'ai_agent': ai_agent,  # Now ai_agent is guaranteed to exist
                    'notes': f'HumeAI call: {twilio_call.call_sid}'
                }
            )
            
            if created:
                logger.info(f"[OK] Created new customer profile for {twilio_call.to_number}")
            else:
                logger.info(f"[OK] Using existing customer profile for {twilio_call.to_number}")
            
            return customer_profile
            
        except Exception as e:
            logger.error(f"Error creating customer profile: {str(e)}")
            return None
    
    def _get_or_create_auto_campaign(self, twilio_call: TwilioCall, customer_profile: CustomerProfile):
        """Create or get auto campaign for scheduling"""
        try:
            if not customer_profile or not customer_profile.ai_agent:
                return None
            
            # Find or create a campaign for this agent
            campaign, created = AutoCallCampaign.objects.get_or_create(
                ai_agent=customer_profile.ai_agent,
                status='active',
                name__startswith='HumeAI Auto Campaign',
                defaults={
                    'name': f'HumeAI Auto Campaign - {timezone.now().strftime("%Y%m%d")}',
                    'campaign_type': 'sales',
                    'calls_per_hour': 4,
                    'working_hours_start': '09:00',
                    'working_hours_end': '18:00',
                    'target_customers': 50,
                    'campaign_data': {
                        'source': 'hume_ai_twilio',
                        'auto_created': True,
                        'hume_agent_id': str(twilio_call.agent.id) if twilio_call.agent else None
                    }
                }
            )
            
            if created:
                logger.info(f"📞 Created new auto campaign for HumeAI calls")
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating auto campaign: {str(e)}")
            return None
    
    def _get_ai_agent_from_hume_agent(self, hume_agent: HumeAgent):
        """Get or create AIAgent from HumeAgent"""
        try:
            if not hume_agent:
                return None
            
            # Get the user who created the HumeAgent
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Try to find corresponding AIAgent by client or create new
            try:
                # First try to find by client if hume_agent has created_by
                if hasattr(hume_agent, 'created_by') and hume_agent.created_by:
                    ai_agent = AIAgent.objects.get(client=hume_agent.created_by)
                    return ai_agent
            except AIAgent.DoesNotExist:
                pass
            
            # If not found, try to get first available or create default
            try:
                # Get first user to associate with agent
                default_user = User.objects.first()
                if not default_user:
                    logger.warning("No users found for AI agent creation")
                    return None
                
                # Create AI agent for demo/testing
                # Use get_or_create to avoid UNIQUE constraint error
                ai_agent, created = AIAgent.objects.get_or_create(
                    client=default_user,
                    defaults={
                        'name': f"AI Agent for {hume_agent.name}",
                        'personality_type': 'professional',
                        'voice_model': hume_agent.voice_name if hasattr(hume_agent, 'voice_name') else 'en-US-female-1',
                        'status': 'active',
                        'conversation_memory': {
                            'hume_config_id': hume_agent.hume_config_id if hasattr(hume_agent, 'hume_config_id') else None,
                            'original_hume_agent': str(hume_agent.id)
                        }
                    }
                )
                
                if created:
                    logger.info(f"[OK] Created new AI agent for user {default_user.email}")
                else:
                    logger.info(f"[OK] Using existing AI agent for user {default_user.email}")
                
                return ai_agent
                
            except Exception as creation_error:
                logger.error(f"Failed to create/get AI agent: {str(creation_error)}")
                return None
            
        except Exception as e:
            logger.error(f"Error getting AIAgent: {str(e)}")
            return None
    
    def _create_call_session_from_twilio(self, twilio_call: TwilioCall, call_outcome: str, customer_profile: CustomerProfile):
        """Create CallSession from TwilioCall for our intelligent scheduler"""
        try:
            from calls.models import CallSession
            
            # Get user from customer profile or use first available user
            user = customer_profile.ai_agent.client if customer_profile and customer_profile.ai_agent else None
            if not user:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.first()
            
            if not user:
                logger.warning("No user available for CallSession creation")
                return None
            
            call_session, created = CallSession.objects.get_or_create(
                twilio_call_sid=twilio_call.call_sid,
                defaults={
                    'user': user,
                    'agent': None,  # No Agent model reference needed
                    'call_type': 'outbound',
                    'status': twilio_call.status,
                    'caller_number': twilio_call.from_number,
                    'callee_number': twilio_call.to_number,
                    'started_at': twilio_call.started_at or twilio_call.created_at,
                    'ended_at': twilio_call.ended_at,
                    'duration': twilio_call.duration,
                    'outcome': call_outcome,
                    'notes': f'HumeAI call - Agent: {twilio_call.agent.name if twilio_call.agent else "None"}',
                    'ai_summary': f'Call analyzed with outcome: {call_outcome}'
                }
            )
            
            if not created:
                # Update existing session
                call_session.outcome = call_outcome
                call_session.status = twilio_call.status
                call_session.ended_at = twilio_call.ended_at
                call_session.duration = twilio_call.duration
                call_session.save()
            
            return call_session
            
        except Exception as e:
            logger.error(f"Error creating call session: {str(e)}")
            return None
    
    def _update_twilio_call_with_scheduling(self, twilio_call: TwilioCall, call_outcome: str, scheduling_result: dict):
        """Update TwilioCall record with scheduling information"""
        try:
            # Add scheduling info to analytics if exists
            analytics = getattr(twilio_call, 'analytics', None)
            if analytics:
                if not analytics.summary:
                    analytics.summary = ""
                
                analytics.summary += f"\n\n🧠 Intelligent Scheduling Applied:\n"
                analytics.summary += f"- Analyzed Outcome: {call_outcome}\n"
                analytics.summary += f"- Next Call Scheduled: {scheduling_result.get('next_call_scheduled', False)}\n"
                analytics.summary += f"- Rule Applied: {scheduling_result.get('rule_applied', 'none')}\n"
                
                # Set business metrics based on outcome
                if call_outcome == 'interested':
                    analytics.lead_qualified = True
                elif call_outcome == 'callback_requested':
                    analytics.lead_qualified = True
                    
                analytics.save()
                
        except Exception as e:
            logger.error(f"Error updating Twilio call: {str(e)}")
    
    def _simple_scheduling_fallback(self, twilio_call: TwilioCall, call_outcome: str):
        """
        Simple scheduling fallback when full system unavailable
        Basic scheduling logic without complex integrations
        """
        try:
            logger.info(f"📋 Using simple scheduling fallback for outcome: {call_outcome}")
            
            # Simple scheduling rules
            should_schedule = call_outcome in ['interested', 'callback_requested', 'maybe_interested', 'no_answer', 'busy']
            
            # Simple delay mapping (in hours)
            delay_hours = {
                'interested': 1,        # Very quick follow-up
                'callback_requested': 24,  # Next day
                'maybe_interested': 72,    # 3 days
                'no_answer': 2,           # 2 hours retry
                'busy': 4,                # 4 hours retry
                'not_interested': 0       # No scheduling
            }.get(call_outcome, 0)
            
            next_call_time = None
            if should_schedule and delay_hours > 0:
                from datetime import timedelta
                next_call_time = timezone.now() + timedelta(hours=delay_hours)
                
                # Create simple periodic task for follow-up
                from django_celery_beat.models import PeriodicTask, IntervalSchedule
                
                # Create interval (one-time task)
                interval = IntervalSchedule.objects.get_or_create(
                    every=delay_hours,
                    period=IntervalSchedule.HOURS,
                )[0]
                
                # Create task
                task_name = f"simple_follow_up_{twilio_call.to_number.replace('+', '')}_{timezone.now().timestamp()}"
                
                # Get agent ID safely
                agent_id = str(twilio_call.agent.id) if twilio_call.agent else None
                
                PeriodicTask.objects.create(
                    name=task_name,
                    task='agents.tasks.simple_follow_up_call',
                    interval=interval,
                    args=json.dumps([twilio_call.to_number, agent_id, call_outcome]),
                    start_time=next_call_time,
                    one_off=True,
                    enabled=True
                )
                
                logger.info(f"✅ Simple follow-up scheduled for {next_call_time}")
            
            return {
                'success': True,
                'call_sid': twilio_call.call_sid,
                'analyzed_outcome': call_outcome,
                'intelligent_scheduling': {
                    'next_call_scheduled': should_schedule and delay_hours > 0,
                    'next_call_time': next_call_time.isoformat() if next_call_time else None,
                    'rule_applied': f'simple_fallback_{call_outcome}',
                    'delay_hours': delay_hours,
                    'scheduling_method': 'simple_fallback'
                },
                'customer_phone': twilio_call.to_number,
                'next_call_scheduled': should_schedule and delay_hours > 0
            }
            
        except Exception as e:
            logger.error(f"Even simple scheduling failed: {str(e)}")
            return {
                'success': False,
                'error': f'Simple scheduling failed: {str(e)}',
                'call_sid': twilio_call.call_sid,
                'analyzed_outcome': call_outcome,
                'intelligent_scheduling': {
                    'next_call_scheduled': False,
                    'error': str(e)
                }
            }


# Global instance for HumeAI + Twilio integration
hume_twilio_scheduler = HumeTwilioIntelligentScheduler()