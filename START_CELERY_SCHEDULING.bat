@echo off
echo ===================================
echo   CELERY SCHEDULING SYSTEM READY
echo ===================================
echo.
echo The scheduled tasks system is working!
echo.
echo Your scheduled tasks:
echo - Auto calls: Every 5 minutes (9 AM - 5 PM)
echo - Callback reminders: Every 10 minutes  
echo - Campaign cleanup: Daily at 2 AM
echo - Customer priorities: Daily at 1 AM
echo.
echo ===================================
echo   STARTING CELERY PROCESSES
echo ===================================
echo.

cd /d %~dp0

echo Starting Celery Worker...
start "Celery Worker" cmd /k "venv\Scripts\activate && python -m celery -A core worker --loglevel=info --pool=solo"

timeout /t 3 /nobreak > nul

echo Starting Celery Beat Scheduler...
start "Celery Beat" cmd /k "venv\Scripts\activate && python -m celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo.
echo ===================================
echo   CELERY STARTED SUCCESSFULLY!
echo ===================================
echo.
echo Two terminal windows should have opened:
echo 1. Celery Worker - processes tasks
echo 2. Celery Beat - handles scheduling
echo.
echo To stop: Close both terminal windows or press Ctrl+C in each
echo.
echo Your auto-call scheduling is now ACTIVE!
echo.
pause