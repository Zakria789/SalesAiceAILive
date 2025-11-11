# READY TO START CELERY! 
# Follow these steps in order:

# Terminal 1 - Start Celery Worker
venv\Scripts\activate
celery -A core worker --loglevel=info --pool=solo

# Terminal 2 - Start Celery Beat (Database Scheduler)  
venv\Scripts\activate
celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Check if tasks are running
celery -A core inspect active

# Manual test a task
python manage.py shell -c "from agents.tasks import process_scheduled_auto_calls; result = process_scheduled_auto_calls.delay(); print('Task queued with ID:', result.id)"

# Check task results
python manage.py shell -c "from django_celery_results.models import TaskResult; print('Recent tasks:'); [print(f'{t.task_name}: {t.status}') for t in TaskResult.objects.all()[:5]]"