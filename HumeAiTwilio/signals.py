"""
Django signals for HumeAI + Twilio Integration

NOTE: HumeAgent sync is now handled directly in views.py (HumeAgentViewSet)
      to avoid signal duplication. These signal handlers are kept for reference
      but are disabled.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import TwilioCall, CallAnalytics, HumeAgent
from .services import AnalyticsService
from .hume_agent_service import hume_agent_service

import logging

logger = logging.getLogger(__name__)


# DISABLED: Agent sync now handled in HumeAgentViewSet.perform_create/update/destroy
# @receiver(post_save, sender=HumeAgent)
def sync_agent_with_hume_DISABLED(sender, instance, created, **kwargs):
    """
    Auto-sync agent with HumeAI when created or updated
    """
    try:
        if created:
            # Create new agent in HumeAI
            logger.info(f"🤖 Creating agent in HumeAI: {instance.name}")
            
            config_id = hume_agent_service.create_agent(
                name=instance.name,
                system_prompt=instance.system_prompt,
                voice_name=instance.voice_name,
                language=instance.language
            )
            
            if config_id:
                # Save HumeAI config_id to local agent
                instance.hume_config_id = config_id
                instance.save(update_fields=['hume_config_id'])
                logger.info(f"✅ Agent synced with HumeAI: {config_id}")
            else:
                logger.error(f"❌ Failed to sync agent with HumeAI: {instance.name}")
                
        else:
            # Update existing agent in HumeAI (if config_id exists)
            if instance.hume_config_id:
                logger.info(f"🔄 Updating agent in HumeAI: {instance.hume_config_id}")
                
                success = hume_agent_service.update_agent(
                    config_id=instance.hume_config_id,
                    name=instance.name,
                    system_prompt=instance.system_prompt,
                    voice_name=instance.voice_name,
                    language=instance.language
                )
                
                if success:
                    logger.info(f"✅ Agent updated in HumeAI: {instance.hume_config_id}")
                else:
                    logger.error(f"❌ Failed to update agent in HumeAI: {instance.hume_config_id}")
                    
    except Exception as e:
        logger.error(f"❌ Error in agent sync signal: {str(e)}")


# DISABLED: Agent delete sync now handled in HumeAgentViewSet.perform_destroy
# @receiver(pre_delete, sender=HumeAgent)
def delete_agent_from_hume_DISABLED(sender, instance, **kwargs):
    """
    Delete agent from HumeAI when local agent is deleted
    """
    try:
        if instance.hume_config_id:
            logger.info(f"🗑️ Deleting agent from HumeAI: {instance.hume_config_id}")
            
            success = hume_agent_service.delete_agent(instance.hume_config_id)
            
            if success:
                logger.info(f"✅ Agent deleted from HumeAI: {instance.hume_config_id}")
            else:
                logger.error(f"❌ Failed to delete agent from HumeAI: {instance.hume_config_id}")
                
    except Exception as e:
        logger.error(f"❌ Error in agent delete signal: {str(e)}")


@receiver(post_save, sender=TwilioCall)
def call_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for when call status changes
    """
    if not created:
        # If call is completed, generate analytics
        if instance.status == 'completed':
            try:
                # Check if analytics already exists
                if not hasattr(instance, 'analytics'):
                    AnalyticsService.calculate_analytics(instance)
                    logger.info(f"Analytics generated for call: {instance.call_sid}")
            except Exception as e:
                logger.error(f"Error generating analytics: {str(e)}")
