from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .ai_agent_models import AIAgent, CustomerProfile, CallSession, ScheduledCallback
from .auto_campaign_models import AutoCallCampaign, AutoCampaignContact

logger = logging.getLogger(__name__)


class IntelligentAutoScheduler:
    """
    Intelligent Auto-Scheduler that schedules calls based on customer responses
    Customer ke response ke base par automatically next calls schedule karta hai
    """
    
    def __init__(self):
        self.response_scheduling_rules = {
            'interested': {
                'follow_up_delay': 30,  # minutes
                'priority': 4,  # High priority
                'call_type': 'follow_up',
                'next_action': 'schedule_immediate_follow_up'
            },
            'callback_requested': {
                'follow_up_delay': 60 * 24,  # 24 hours
                'priority': 4,  # High priority
                'call_type': 'callback',
                'next_action': 'schedule_callback'
            },
            'maybe_interested': {
                'follow_up_delay': 60 * 48,  # 2 days
                'priority': 3,  # Medium priority
                'call_type': 'follow_up',
                'next_action': 'schedule_nurture_call'
            },
            'not_interested': {
                'follow_up_delay': 60 * 24 * 30,  # 30 days
                'priority': 1,  # Low priority
                'call_type': 'long_term_follow_up',
                'next_action': 'schedule_long_term_follow_up'
            },
            'no_answer': {
                'follow_up_delay': 120,  # 2 hours
                'priority': 2,  # Medium priority
                'call_type': 'retry',
                'next_action': 'schedule_retry'
            },
            'busy': {
                'follow_up_delay': 240,  # 4 hours
                'priority': 2,  # Medium priority
                'call_type': 'retry',
                'next_action': 'schedule_retry'
            }
        }
    
    def process_call_outcome_and_schedule(self, call_session: CallSession, campaign: AutoCallCampaign = None):
        """
        Process call outcome and automatically schedule next calls
        Call ka result dekh kar next call schedule karta hai
        """
        try:
            outcome = call_session.outcome
            customer = call_session.customer_profile
            agent = call_session.ai_agent
            
            logger.info(f"🧠 Processing call outcome: {outcome} for {customer.phone_number}")
            
            # Get scheduling rule based on outcome
            rule = self.response_scheduling_rules.get(outcome, self.response_scheduling_rules['no_answer'])
            
            # Update customer interest level based on response
            self._update_customer_interest_level(customer, outcome)
            
            # Schedule next action based on outcome
            next_call_scheduled = False
            
            if rule['next_action'] == 'schedule_immediate_follow_up':
                next_call_scheduled = self._schedule_immediate_follow_up(agent, customer, campaign, rule)
                
            elif rule['next_action'] == 'schedule_callback':
                next_call_scheduled = self._schedule_callback(agent, customer, call_session, rule)
                
            elif rule['next_action'] == 'schedule_nurture_call':
                next_call_scheduled = self._schedule_nurture_call(agent, customer, campaign, rule)
                
            elif rule['next_action'] == 'schedule_long_term_follow_up':
                next_call_scheduled = self._schedule_long_term_follow_up(agent, customer, campaign, rule)
                
            elif rule['next_action'] == 'schedule_retry':
                next_call_scheduled = self._schedule_retry_call(agent, customer, campaign, rule)
            
            # Log the intelligent scheduling result
            if next_call_scheduled:
                logger.info(f"✅ Intelligently scheduled next call for {customer.phone_number} based on '{outcome}' response")
            
            return {
                'success': True,
                'outcome_processed': outcome,
                'next_call_scheduled': next_call_scheduled,
                'rule_applied': rule['next_action'],
                'customer_updated': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process call outcome: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_customer_interest_level(self, customer: CustomerProfile, outcome: str):
        """Update customer interest level based on call outcome"""
        try:
            old_level = customer.interest_level
            
            if outcome == 'interested':
                customer.interest_level = 'hot'
            elif outcome == 'callback_requested':
                customer.interest_level = 'hot'
            elif outcome == 'maybe_interested':
                customer.interest_level = 'warm'
            elif outcome == 'not_interested':
                customer.interest_level = 'cold'
            elif outcome in ['no_answer', 'busy']:
                # Keep same level, just update last interaction
                pass
            
            customer.last_interaction = timezone.now()
            customer.save()
            
            if old_level != customer.interest_level:
                logger.info(f"📊 Updated customer {customer.phone_number}: {old_level} → {customer.interest_level}")
            
        except Exception as e:
            logger.error(f"Failed to update customer interest level: {str(e)}")
    
    def _schedule_immediate_follow_up(self, agent: AIAgent, customer: CustomerProfile, 
                                    campaign: AutoCallCampaign, rule: dict) -> bool:
        """Schedule immediate follow-up for interested customers"""
        try:
            follow_up_time = timezone.now() + timedelta(minutes=rule['follow_up_delay'])
            
            if campaign:
                # Add to existing campaign
                contact = AutoCampaignContact.objects.create(
                    campaign=campaign,
                    customer_profile=customer,
                    status='pending',
                    priority=rule['priority'],
                    scheduled_datetime=follow_up_time,
                    call_outcome='follow_up_scheduled'
                )
                logger.info(f"🚀 Immediate follow-up scheduled in {rule['follow_up_delay']} minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to schedule immediate follow-up: {str(e)}")
            return False
    
    def _schedule_callback(self, agent: AIAgent, customer: CustomerProfile, 
                         call_session: CallSession, rule: dict) -> bool:
        """Schedule callback for customers who requested callback"""
        try:
            callback_time = timezone.now() + timedelta(minutes=rule['follow_up_delay'])
            
            # Create scheduled callback
            ScheduledCallback.objects.create(
                ai_agent=agent,
                customer_profile=customer,
                scheduled_datetime=callback_time,
                status='scheduled',
                reason=f"Customer requested callback after call at {call_session.initiated_at}",
                call_session=call_session
            )
            
            logger.info(f"📞 Callback scheduled for {callback_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule callback: {str(e)}")
            return False
    
    def _schedule_nurture_call(self, agent: AIAgent, customer: CustomerProfile, 
                             campaign: AutoCallCampaign, rule: dict) -> bool:
        """Schedule nurture call for maybe interested customers"""
        try:
            nurture_time = timezone.now() + timedelta(minutes=rule['follow_up_delay'])
            
            if campaign:
                # Add to existing campaign with lower priority
                contact = AutoCampaignContact.objects.create(
                    campaign=campaign,
                    customer_profile=customer,
                    status='pending',
                    priority=rule['priority'],
                    scheduled_datetime=nurture_time,
                    call_outcome='nurture_scheduled'
                )
                logger.info(f"🌱 Nurture call scheduled in {rule['follow_up_delay']} minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to schedule nurture call: {str(e)}")
            return False
    
    def _schedule_long_term_follow_up(self, agent: AIAgent, customer: CustomerProfile, 
                                    campaign: AutoCallCampaign, rule: dict) -> bool:
        """Schedule long-term follow-up for not interested customers"""
        try:
            long_term_time = timezone.now() + timedelta(minutes=rule['follow_up_delay'])
            
            if campaign:
                # Add to campaign with very low priority
                contact = AutoCampaignContact.objects.create(
                    campaign=campaign,
                    customer_profile=customer,
                    status='pending',
                    priority=rule['priority'],
                    scheduled_datetime=long_term_time,
                    call_outcome='long_term_scheduled'
                )
                logger.info(f"🕐 Long-term follow-up scheduled in {rule['follow_up_delay']} minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to schedule long-term follow-up: {str(e)}")
            return False
    
    def _schedule_retry_call(self, agent: AIAgent, customer: CustomerProfile, 
                           campaign: AutoCallCampaign, rule: dict) -> bool:
        """Schedule retry call for no answer/busy customers"""
        try:
            retry_time = timezone.now() + timedelta(minutes=rule['follow_up_delay'])
            
            if campaign:
                # Add retry to campaign
                contact = AutoCampaignContact.objects.create(
                    campaign=campaign,
                    customer_profile=customer,
                    status='pending',
                    priority=rule['priority'],
                    scheduled_datetime=retry_time,
                    call_outcome='retry_scheduled'
                )
                logger.info(f"🔄 Retry call scheduled in {rule['follow_up_delay']} minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to schedule retry call: {str(e)}")
            return False
    
    def get_scheduling_rules(self):
        """Get current scheduling rules for API/display"""
        return self.response_scheduling_rules
    
    def update_scheduling_rule(self, outcome: str, new_rule: dict):
        """Update scheduling rule for specific outcome"""
        if outcome in self.response_scheduling_rules:
            self.response_scheduling_rules[outcome].update(new_rule)
            logger.info(f"📋 Updated scheduling rule for '{outcome}': {new_rule}")
            return True
        return False


# Global instance
intelligent_scheduler = IntelligentAutoScheduler()