#!/usr/bin/env python
import os
import django

# Set up Django manually without .env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('CELERY_BROKER_URL', 'memory://')  # Use in-memory broker for test
os.environ.setdefault('CELERY_RESULT_BACKEND', 'django-db')

django.setup()

# Test Celery task
try:
    from agents.tasks import process_scheduled_auto_calls
    print("✅ Task imported successfully")
    
    # Test task execution
    result = process_scheduled_auto_calls()
    print(f"✅ Task executed successfully: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test DatabaseScheduler
try:
    from django_celery_beat.models import PeriodicTask
    tasks = PeriodicTask.objects.all()
    print(f"✅ Found {tasks.count()} periodic tasks in database:")
    for task in tasks:
        print(f"  - {task.name}: {task.enabled}")
        
except Exception as e:
    print(f"❌ Database scheduler error: {e}")