@echo off
echo ========================================
echo    Django Backend Auto Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ first
    pause
    exit /b 1
)

echo [1/7] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/7] Installing requirements...
echo Installing core requirements...
pip install -r requirements-core.txt
if errorlevel 1 (
    echo ERROR: Failed to install core requirements
    pause
    exit /b 1
)

set /p install_full="Install full requirements with all features? (y/n): "
if /i "%install_full%"=="y" (
    echo Installing full requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Some optional packages failed to install
        echo Core functionality will still work
    )
) else (
    echo ✅ Core requirements installed. You can install full requirements later with: pip install -r requirements.txt
)

echo [4/7] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo ✅ .env file created from .env.example
    echo ⚠️  Please edit .env file with your settings
) else (
    echo ✅ .env file already exists
)

echo [5/7] Running database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Database migration failed
    pause
    exit /b 1
)

echo [6/7] Creating admin user...
echo.
set /p create_admin="Create admin user now? (y/n): "
if /i "%create_admin%"=="y" (
    python manage.py create_admin --email=admin@gmail.com --password=admin123 --name="Admin User"
    echo ✅ Admin user created: admin@gmail.com / admin123
) else (
    echo ⚠️  You can create admin later with: python manage.py createsuperuser
)

echo.
echo [7/7] Setup complete! 🎉
echo.
echo ========================================
echo     🚀 Quick Start Commands
echo ========================================
echo To start server: python manage.py runserver
echo.
echo 📱 Access Points:
echo • API Docs: http://127.0.0.1:8000/swagger/
echo • Admin: http://127.0.0.1:8000/admin/
echo • API: http://127.0.0.1:8000/api/
echo.
echo 🔐 Default Admin:
echo • Email: admin@gmail.com
echo • Password: admin123
echo ========================================
echo.
set /p start_server="Start server now? (y/n): "
if /i "%start_server%"=="y" (
    echo Starting Django server...
    python manage.py runserver
) else (
    echo Run 'python manage.py runserver' when ready!
    pause
)
