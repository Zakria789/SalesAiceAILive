"""
Build-time Django settings for Railway
Only used during collectstatic - no database required
"""
from .settings import *

# Override database to use SQLite for build time only
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable database operations during build
DATABASE_URL = None
RAILWAY_ENVIRONMENT = 'build'

# Minimal apps for collectstatic
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
]

# Skip problematic middleware during build
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

print("🔨 Using build-time settings - SQLite in-memory database")