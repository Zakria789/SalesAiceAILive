# 🚀 Django Backend Setup Guide

Ye guide follow karke aap is project ko kisi bhi machine par run kar sakte hain.

## 📋 Prerequisites

- Python 3.8+ installed
- Git installed
- Virtual environment support

## 🛠️ Setup Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd TestRepo
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**Option A: Core requirements only (recommended for beginners)**
```bash
pip install -r requirements-core.txt
```

**Option B: Full requirements (all features)**
```bash
pip install -r requirements.txt
```

**Option C: Development setup**
```bash
pip install -r requirements-core.txt
pip install -r requirements-dev.txt
```

See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed package information.

### 4. Environment Configuration
```bash
# Copy environment file
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux

# Edit .env file with your settings
```

Required .env settings:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings (for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:3000
```

### 5. Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 6. Create Admin User
```bash
# Method 1: Interactive superuser creation
python manage.py createsuperuser

# Method 2: Quick admin creation
python manage.py create_admin --email=admin@gmail.com --password=admin123 --name="Admin User"
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## 🌐 Access Points

After running the server:

- **Main API**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/swagger/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **ReDoc**: http://127.0.0.1:8000/redoc/

## 🔐 Default Credentials

If you used the quick setup:
- **Email**: admin@gmail.com
- **Password**: admin123

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/password-reset/` - Request password reset

### User Management
- `GET /api/accounts/me/` - Current user info
- `GET /api/accounts/profile/` - User profile
- `GET /api/accounts/users/` - List users (Admin only)
- `POST /api/accounts/change-role/` - Change user role (Admin only)

## 🧪 Testing the API

### 1. Using Swagger UI
1. Go to http://127.0.0.1:8000/swagger/
2. Use `/api/auth/register/` to create a user
3. Use `/api/auth/login/` to get JWT token
4. Click "Authorize" button and enter: `Bearer your-token`
5. Test protected endpoints

### 2. Using curl
```bash
# Register user
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Use token for protected endpoint
curl -X GET http://127.0.0.1:8000/api/accounts/me/ \
  -H "Authorization: Bearer your-access-token"
```

## 🗂️ Project Structure
```
├── core/                   # Main project settings
├── accounts/              # User management
├── authentication/       # Auth endpoints
├── templates/            # Email templates
├── static/              # Static files
├── media/               # Uploaded files
├── requirements.txt     # Dependencies
├── .env.example        # Environment template
└── manage.py           # Django management
```

## 🛡️ Security Notes

1. Change `SECRET_KEY` in production
2. Set `DEBUG=False` in production
3. Configure proper email service
4. Use strong passwords
5. Set up HTTPS in production

## 🚀 Production Deployment

For production deployment:

1. Set environment variables:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

2. Configure database (PostgreSQL recommended):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

3. Set up static files:
```bash
python manage.py collectstatic
```

4. Use production WSGI server (gunicorn, uWSGI)

## 🆘 Troubleshooting

### Common Issues:

1. **Module not found error**:
```bash
pip install -r requirements.txt
```

2. **Database errors**:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Permission denied**:
```bash
python manage.py createsuperuser
```

4. **Email not working**:
- Check .env email settings
- Use app-specific password for Gmail
- In development, check console output

## 📞 Support

If you face any issues:
1. Check error logs
2. Verify .env configuration
3. Ensure all dependencies are installed
4. Check Python version compatibility

---

**Happy Coding! 🎉**
