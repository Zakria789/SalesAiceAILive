# 🔧 Railway PostgreSQL Database Access Guide

## Problem ye thi:
- Railway build time pe `postgres.railway.internal` hostname available nahi hai
- Migrations build time pe run kar rahe the, runtime pe nahi
- `railway.json` me migrations build command me the instead of start command

## ✅ Fixed Issues:
1. Migrations ab runtime pe chalenge (start command me)
2. Build time pe sirf static files collect honge
3. Database connection runtime pe hoga jab PostgreSQL service available hai

---

## 🔍 How to Access PostgreSQL on Railway

### Method 1: Railway Dashboard SQL Editor (Easiest)
```
1. Railway dashboard → Your Project → Services → PostgreSQL service
2. Click "Database" tab ya "Connect" section
3. Railway ka built-in SQL editor use karo
4. Direct SQL queries run kar sakte ho
```

### Method 2: psql Client (Terminal)
```powershell
# Install PostgreSQL client (if not installed)
# Windows: Download from postgresql.org
# Or use Docker:
docker run --rm -it postgres:15 psql "postgresql://postgres:aekMHrudKAujopHjwQYTEZYNofYrN@postgres.railway.internal:5432/railway"
```

### Method 3: GUI Tools
- **pgAdmin**: Popular PostgreSQL GUI
- **DBeaver**: Free universal database tool  
- **TablePlus**: macOS/Windows GUI
- **DataGrip**: JetBrains database IDE

---

## 📋 Essential SQL Queries

### 1. List All Tables
```sql
-- Check karo ke Django tables exist hain
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### 2. Find User Table
```sql
-- Django default table ya custom user model check karo
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE '%user%' 
AND table_schema = 'public';
```

### 3. Check User Table Structure  
```sql
-- Replace 'accounts_user' with actual table name
\d accounts_user

-- Ya SQL me:
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'accounts_user' 
ORDER BY ordinal_position;
```

### 4. Find Specific User
```sql
-- Check if user exists and current permissions
SELECT id, email, is_staff, is_superuser, is_active, date_joined
FROM accounts_user 
WHERE email = 'SalesAice.ai@gmail.com';
```

### 5. Promote User to Admin (SAFE WAY)
```sql
-- First check current status
SELECT id, email, is_staff, is_superuser 
FROM accounts_user 
WHERE email = 'SalesAice.ai@gmail.com';

-- If user exists, promote to admin
UPDATE accounts_user 
SET is_staff = TRUE, is_superuser = TRUE 
WHERE email = 'SalesAice.ai@gmail.com';

-- Verify the change
SELECT id, email, is_staff, is_superuser 
FROM accounts_user 
WHERE email = 'SalesAice.ai@gmail.com';
```

### 6. Create New Admin User (SQL - Not Recommended)
```sql
-- Better to use Django management commands
-- But if you must use SQL:
INSERT INTO accounts_user (
    email, 
    password, 
    is_staff, 
    is_superuser, 
    is_active, 
    date_joined
) VALUES (
    'admin@example.com',
    'pbkdf2_sha256$...',  -- Need proper password hash
    TRUE,
    TRUE, 
    TRUE,
    NOW()
);
```

---

## 🚀 Recommended Django Commands (Safer)

### 1. Run Migrations
```powershell
railway run python manage.py migrate
```

### 2. Create Superuser
```powershell
railway run python manage.py createsuperuser --email SalesAice.ai@gmail.com
```

### 3. Use Our Custom Script
```powershell
railway run python make_user_admin.py "SalesAice.ai@gmail.com"
```

### 4. List All Users
```powershell
railway run python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
for u in User.objects.all():
    print(f'{u.email}: staff={u.is_staff}, super={u.is_superuser}')
"
```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "could not translate host name"
```
Problem: DATABASE_URL hostname not resolvable
Solution: Use Railway CLI commands, not direct psql from local machine
```

### Issue 2: Table doesn't exist
```sql
-- Check if migrations ran
SELECT * FROM django_migrations ORDER BY applied DESC LIMIT 5;

-- If no tables, run migrations:
-- railway run python manage.py migrate
```

### Issue 3: Wrong table name
```sql
-- Find actual table name
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE '%user%' AND table_schema = 'public';
```

### Issue 4: Permission denied
```
Problem: Database user doesn't have required permissions
Solution: Railway PostgreSQL user should have full access by default
Check: Railway dashboard → PostgreSQL → Variables → Verify DATABASE_URL
```

### Issue 5: Still using SQLite
```
Check environment variables in Railway dashboard:
- RAILWAY_ENVIRONMENT=production ✅
- DATABASE_URL=postgresql://... ✅

If missing, add them and redeploy.
```

---

## 📊 Complete Verification Steps

### 1. Check Environment
```powershell
railway run python -c "
import os
print('RAILWAY_ENVIRONMENT:', os.getenv('RAILWAY_ENVIRONMENT'))
print('DATABASE_URL exists:', bool(os.getenv('DATABASE_URL')))
from django.conf import settings
print('Database engine:', settings.DATABASES['default']['ENGINE'])
"
```

### 2. Test Database Connection
```powershell
railway run python debug_db_connection.py
```

### 3. Verify User Permissions
```powershell
railway run python make_user_admin.py "SalesAice.ai@gmail.com"
```

### 4. Test Admin Access
```
1. Open: https://your-app.up.railway.app/admin/
2. Login with promoted user
3. Should have full admin access
```

---

## ⚠️ Security Notes

1. **Never commit DATABASE_URL** in code
2. **Use Django ORM** instead of raw SQL when possible  
3. **Test changes** in development first
4. **Backup important data** before making changes
5. **Use environment variables** for sensitive information

---

## 🎯 Quick Fix Summary

**Problem**: Railway build failing due to DATABASE_URL not available during build

**Solution**: 
1. ✅ Updated `railway.json` - migrations now run at startup
2. ✅ Build only installs packages and collects static files
3. ✅ Database connection happens at runtime when PostgreSQL is available

**Next Steps**:
1. Push updated code: `git push`
2. Wait for deployment
3. Run: `railway run python make_user_admin.py "SalesAice.ai@gmail.com"`
4. Access admin: `https://your-app.up.railway.app/admin/`