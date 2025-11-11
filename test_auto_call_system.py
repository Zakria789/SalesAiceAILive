#!/usr/bin/env python
"""
Test the complete auto-call scheduling system
"""
import os
import django
from django.utils import timezone
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_auto_call_system():
    """Test the complete auto-call scheduling system"""
    
    print("🔍 Testing Auto-Call Scheduling System...")
    print("=" * 50)
    
    # Import models
    from agents.ai_agent_models import AIAgent, CustomerProfile
    from agents.auto_campaign_models import AutoCallCampaign, AutoCampaignContact
    from django_celery_beat.models import PeriodicTask
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # 1. Check if we have users and agents
    user_count = User.objects.count()
    agent_count = AIAgent.objects.count()
    print(f"👤 Users: {user_count}, AI Agents: {agent_count}")
    
    # 2. Check periodic tasks
    active_tasks = PeriodicTask.objects.filter(enabled=True)
    print(f"📅 Active scheduled tasks: {active_tasks.count()}")
    for task in active_tasks:
        print(f"   - {task.name}")
    
    # 3. Check current campaigns
    campaigns = AutoCallCampaign.objects.all()
    print(f"📞 Auto-call campaigns: {campaigns.count()}")
    
    # 4. Check customers
    customers = CustomerProfile.objects.count()
    print(f"👥 Customer profiles: {customers}")
    
    # 5. Test task execution
    print("\n🚀 Testing task execution...")
    try:
        from agents.tasks import process_scheduled_auto_calls
        result = process_scheduled_auto_calls()
        print(f"✅ Auto-call task executed: {result}")
    except Exception as e:
        print(f"❌ Task execution failed: {e}")
    
    # 6. Show next steps
    print("\n📋 Status Summary:")
    if agent_count == 0:
        print("❌ No AI agents found - create agents first")
        print("   → Use Django admin or API to create AI agents")
    
    if customers == 0:
        print("❌ No customers found - add customer profiles")
        print("   → Use Django admin or API to add customers")
    
    if campaigns.filter(status='active').count() == 0:
        print("📝 No active campaigns - auto-calls won't start until campaigns are created")
        print("   → Use the management command: python manage.py start_auto_calls --user-email your@email.com")
    
    if active_tasks.count() == 4:
        print("✅ Scheduling system is configured correctly!")
        print("✅ Run START_CELERY_SCHEDULING.bat to activate scheduling")
    
    print("\n" + "=" * 50)
    print("🎯 Auto-call scheduling system check complete!")

if __name__ == "__main__":
    test_auto_call_system()