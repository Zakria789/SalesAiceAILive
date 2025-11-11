@echo off
echo ================================================================================
echo RESTARTING DJANGO SERVER WITH ALL FIXES
echo ================================================================================
echo.
echo [*] Stopping any existing Django processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *runserver*" 2>nul
timeout /t 2 >nul

echo [*] Starting Django server on port 8002...
cd /d E:\Python-AI\Django-Backend\TESTREPO
call venv\Scripts\activate
start "Django Server" cmd /k "python manage.py runserver 8002"

timeout /t 5 >nul
echo.
echo ================================================================================
echo [+] Django server started!
echo [+] Server URL: http://localhost:8002
echo [+] Ngrok URL: https://uncontortioned-na-ponderously.ngrok-free.dev
echo.
echo [*] Now you can run: python quick_test.py
echo ================================================================================
