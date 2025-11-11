#!/bin/bash

echo "========================================"
echo "    Django Backend Auto Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo -e "${GREEN}[1/7] Creating virtual environment...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}[2/7] Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${GREEN}[3/7] Installing requirements...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install requirements${NC}"
    exit 1
fi

echo -e "${GREEN}[4/7] Setting up environment file...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created from .env.example${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your settings${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo -e "${GREEN}[5/7] Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Database migration failed${NC}"
    exit 1
fi

echo -e "${GREEN}[6/7] Creating admin user...${NC}"
echo ""
read -p "Create admin user now? (y/n): " create_admin
if [[ $create_admin =~ ^[Yy]$ ]]; then
    python manage.py create_admin --email=admin@gmail.com --password=admin123 --name="Admin User"
    echo -e "${GREEN}✅ Admin user created: admin@gmail.com / admin123${NC}"
else
    echo -e "${YELLOW}⚠️  You can create admin later with: python manage.py createsuperuser${NC}"
fi

echo ""
echo -e "${GREEN}[7/7] Setup complete! 🎉${NC}"
echo ""
echo "========================================"
echo "     🚀 Quick Start Commands"
echo "========================================"
echo "To start server: python manage.py runserver"
echo ""
echo "📱 Access Points:"
echo "• API Docs: http://127.0.0.1:8000/swagger/"
echo "• Admin: http://127.0.0.1:8000/admin/"
echo "• API: http://127.0.0.1:8000/api/"
echo ""
echo "🔐 Default Admin:"
echo "• Email: admin@gmail.com"
echo "• Password: admin123"
echo "========================================"
echo ""

read -p "Start server now? (y/n): " start_server
if [[ $start_server =~ ^[Yy]$ ]]; then
    echo "Starting Django server..."
    python manage.py runserver
else
    echo "Run 'python manage.py runserver' when ready!"
fi
