#!/usr/bin/env python
"""
Test Celery scheduling system directly
Bypasses .env file parsing issues
"""

import os
import sys
import django
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('CELERY_BROKER_URL', 'memory://')
os.environ.setdefault('CELERY_RESULT_BACKEND', 'django-db')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test importing tasks
    from agents.tasks import process_scheduled_auto_calls, process_callback_reminders
    print("✅ Tasks imported successfully")
    
    # Test database models
    from agents.auto_campaign_models import AutoCallCampaign, AutoCampaignContact
    from agents.ai_agent_models import AIAgent, CustomerProfile
    print("✅ Models imported successfully")
    
    # Check existing campaigns
    campaign_count = AutoCallCampaign.objects.count()
    print(f"📊 Found {campaign_count} campaigns in database")
    
    # Check agents and customers
    agent_count = AIAgent.objects.count()
    customer_count = CustomerProfile.objects.count()
    print(f"👤 Found {agent_count} agents and {customer_count} customers")
    
    # Test task execution
    print("\n🚀 Testing task execution...")
    result = process_scheduled_auto_calls()
    print(f"✅ Auto calls task result: {result}")
    
    result2 = process_callback_reminders()
    print(f"✅ Callback reminders task result: {result2}")
    
    # Test periodic tasks
    from django_celery_beat.models import PeriodicTask
    periodic_tasks = PeriodicTask.objects.filter(enabled=True)
    print(f"\n📅 Active periodic tasks: {periodic_tasks.count()}")
    for task in periodic_tasks:
        print(f"  - {task.name}: {task.task}")
        
    print("\n✅ All tests passed! Celery scheduling should work.")
    print("\nNext steps:")
    print("1. Fix .env file parsing issue")
    print("2. Start Celery worker: celery -A core worker")
    print("3. Start Celery beat: celery -A core beat --scheduler django_celery_beat.schedulers:DatabaseScheduler")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()