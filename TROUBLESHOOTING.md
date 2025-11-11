# 🚨 Quick Fix for Clone Setup Error

## Error: `ModuleNotFoundError: No module named 'drf_yasg'`

Ye error tab aata hai jab project clone karne ke baad dependencies install nahi kiye.

## ⚡ Quick Fix Commands

Clone kiye gaye project folder mein jakar ye commands run kariye:

### Windows:
```bash
# 1. Virtual environment create karo
python -m venv venv

# 2. Virtual environment activate karo
venv\Scripts\activate

# 3. Core dependencies install karo
pip install -r requirements-core.txt

# 4. Agar full features chahiye
pip install -r requirements.txt

# 5. Database setup
python manage.py makemigrations
python manage.py migrate

# 6. Admin user create karo
python manage.py create_admin --email=admin@gmail.com --password=admin123 --name="Admin User"

# 7. Server run karo
python manage.py runserver
```

### Linux/Mac:
```bash
# 1. Virtual environment create karo
python3 -m venv venv

# 2. Virtual environment activate karo
source venv/bin/activate

# 3. Core dependencies install karo
pip install -r requirements-core.txt

# 4. Database setup
python manage.py makemigrations
python manage.py migrate

# 5. Admin user create karo
python manage.py create_admin --email=admin@gmail.com --password=admin123 --name="Admin User"

# 6. Server run karo
python manage.py runserver
```

## 🎯 Automatic Setup (Recommended)

### Windows:
```bash
# Automatic setup script run karo
setup.bat
```

### Linux/Mac:
```bash
# Executable permission do
chmod +x setup.sh

# Script run karo
./setup.sh
```

## 📋 Step by Step Manual Fix

1. **Virtual Environment Check:**
   ```bash
   # Check if venv is activated
   which python  # Linux/Mac
   where python  # Windows
   ```

2. **Install Missing Package:**
   ```bash
   pip install drf-yasg
   ```

3. **Install All Dependencies:**
   ```bash
   # Core only (recommended)
   pip install -r requirements-core.txt
   
   # Or full setup
   pip install -r requirements.txt
   ```

4. **Environment File:**
   ```bash
   # Copy environment template
   copy .env.example .env     # Windows
   cp .env.example .env       # Linux/Mac
   ```

5. **Database Migration:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Admin:**
   ```bash
   python manage.py create_admin --email=admin@gmail.com --password=admin123 --name="Admin"
   ```

## 🔧 Common Issues & Solutions

### Issue 1: Virtual Environment Not Activated
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Issue 2: Python Version Mismatch
```bash
# Check Python version (should be 3.8+)
python --version

# Use specific Python version if needed
python3.12 -m venv venv
```

### Issue 3: Permission Issues (Linux/Mac)
```bash
sudo chmod +x setup.sh
sudo pip install -r requirements-core.txt
```

### Issue 4: Package Installation Fails
```bash
# Update pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements-core.txt
```

## ✅ Verification Commands

After setup, verify everything works:

```bash
# Check if Django can start
python manage.py check

# Check installed packages
pip list

# Test server start
python manage.py runserver
```

## 🎉 Success Indicators

After successful setup you should see:
- ✅ No import errors
- ✅ Server starts at `http://127.0.0.1:8000/`
- ✅ Swagger docs at `http://127.0.0.1:8000/swagger/`
- ✅ Admin panel at `http://127.0.0.1:8000/admin/`

---

**Run these commands in your cloned project directory and the error will be fixed! 🚀**
<!-- https://chatgpt.com/share/68f63c26-d5cc-8000-b621-b43dd1cc678d-->
<!-- https://chatgpt.com/share/68f63c26-d5cc-8000-b621-b43dd1cc678d -->
