# Railway.app Deployment - Installation & Setup Summary

## 📦 What Was Installed/Added:

### 1. Python Packages Added to `requirements.txt`:
```
dj-database-url==2.1.0    # PostgreSQL connection handling
whitenoise==6.8.2          # Static file serving
psycopg2-binary==2.9.9     # PostgreSQL adapter (will add next)
```

### 2. Configuration Files Created:
```
✅ railway.json           # Railway build & deploy config
✅ nixpacks.toml          # Python environment setup
✅ .railwayignore         # Files to exclude from deploy
✅ .env.railway.template  # Environment variables template
```

### 3. Documentation Files Created:
```
✅ RAILWAY_DEPLOYMENT_GUIDE.md  # Complete deployment guide
✅ RAILWAY_QUICK_START.md       # 5-minute quick start
✅ RAILWAY_SETUP_SUMMARY.md     # This file
```

### 4. Modified Files:
```
✅ Procfile               # Added worker & beat processes
✅ runtime.txt            # Changed to Python 3.11.8 (Railway compatible)
✅ core/settings.py       # Added Railway support
```

---

## 🔧 Settings.py Changes Made:

### 1. **Railway Environment Detection:**
```python
RAILWAY_ENVIRONMENT = config('RAILWAY_ENVIRONMENT', default='')
if RAILWAY_ENVIRONMENT == 'production':
    # Production settings
else:
    # Development settings
```

### 2. **Dynamic ALLOWED_HOSTS:**
```python
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app',
    RAILWAY_PUBLIC_DOMAIN,
    RAILWAY_PRIVATE_DOMAIN,
]
```

### 3. **PostgreSQL Database Support:**
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

### 4. **WhiteNoise for Static Files:**
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added
    # ... other middleware
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### 5. **Production Security:**
```python
if RAILWAY_ENVIRONMENT == 'production':
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## 🚀 Deployment Architecture:

```
┌─────────────────────────────────────────────────┐
│            Railway.app Platform                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Web App    │  │  PostgreSQL  │            │
│  │   (Daphne)   │──│   Database   │            │
│  │   Port:8000  │  │              │            │
│  └──────────────┘  └──────────────┘            │
│         │                                        │
│         │          ┌──────────────┐            │
│         └──────────│    Redis     │            │
│                    │  (Cache/WS)  │            │
│                    └──────────────┘            │
│                           │                     │
│         ┌─────────────────┴─────────────┐      │
│         │                               │      │
│  ┌──────────────┐              ┌──────────────┐│
│  │Celery Worker │              │ Celery Beat  ││
│  │(Background)  │              │ (Scheduler)  ││
│  └──────────────┘              └──────────────┘│
│                                                 │
└─────────────────────────────────────────────────┘
         │
         │ HTTPS (Auto SSL)
         │
         ▼
┌─────────────────────┐
│   Frontend App      │
│  (Vercel/Netlify)   │
└─────────────────────┘
```

---

## 📋 Services Required on Railway:

### Service 1: **Main Web App** (Auto-created)
- **Type:** Web Service
- **Source:** GitHub repo
- **Build:** Automatic (nixpacks)
- **Start:** `daphne -b 0.0.0.0 -p $PORT core.asgi:application`
- **Environment:** All variables from `.env.railway.template`

### Service 2: **PostgreSQL Database**
- **Type:** Database
- **Add:** Railway Dashboard → New → Database → PostgreSQL
- **Auto-provides:** `DATABASE_URL`

### Service 3: **Redis Database**
- **Type:** Database  
- **Add:** Railway Dashboard → New → Database → Redis
- **Auto-provides:** `REDIS_URL`
- **Used for:** Celery, Channels (WebSocket), Caching

### Service 4: **Celery Worker**
- **Type:** Worker Service
- **Add:** Railway Dashboard → New → Empty Service
- **Start:** `celery -A core worker --loglevel=info`
- **Environment:** Same as Web App (shared)

### Service 5: **Celery Beat**
- **Type:** Worker Service
- **Add:** Railway Dashboard → New → Empty Service
- **Start:** `celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
- **Environment:** Same as Web App (shared)

---

## 💰 Cost Estimation:

### Free Tier (Hobby):
- **Credit:** $5/month
- **RAM:** 512 MB per service
- **Services:** 2-3 services fit in free tier
- **Execution Time:** 500 hours/month
- **Good for:** Testing, small projects

### Estimated Usage:
```
Web App:        ~$3/month  (always running)
PostgreSQL:     ~$2/month  (minimal data)
Redis:          ~$1/month  (cache only)
Celery Worker:  ~$2/month  (low traffic)
Celery Beat:    ~$1/month  (scheduler)
─────────────────────────────
Total:          ~$9/month  (need $5 Hobby plan)
```

**Recommendation:** Start with Hobby plan ($5/month + $5 credit = $10 total)

---

## 🔄 Auto-Deployment Workflow:

```
Local Development
      ↓
   git add .
   git commit -m "..."
   git push origin main
      ↓
GitHub Repository
      ↓
Railway Webhook Triggered
      ↓
Build Process:
  1. Pull latest code
  2. Install dependencies (requirements.txt)
  3. Collect static files
  4. Run migrations
  5. Start services
      ↓
Deployment Complete
      ↓
Live at: https://your-project.up.railway.app
```

---

## ✅ Pre-Deployment Checklist:

Before deploying, verify:

- [ ] All `requirements.txt` dependencies correct
- [ ] `.env` file has all required variables
- [ ] `SECRET_KEY` is strong (not default)
- [ ] `DEBUG=False` in production
- [ ] Database migrations are up to date locally
- [ ] Static files working locally
- [ ] Twilio credentials valid
- [ ] HumeAI credentials valid
- [ ] Stripe credentials valid (test/live mode)
- [ ] Git repository clean (no sensitive data)

---

## 🧪 Testing After Deployment:

```bash
# 1. Check health
curl https://your-project.up.railway.app/admin/

# 2. Check API
curl https://your-project.up.railway.app/api/

# 3. Check WebSocket (use wscat)
wscat -c wss://your-project.up.railway.app/ws/

# 4. Check database
railway run python manage.py dbshell

# 5. Check logs
railway logs --follow
```

---

## 🐛 Debugging Commands:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login & link project
railway login
railway link

# View logs
railway logs
railway logs --follow
railway logs --service celery-worker

# Run Django commands
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py shell
railway run python manage.py collectstatic

# Check environment
railway run env

# SSH into container (debugging)
railway shell
```

---

## 📊 Monitoring & Alerts:

### Built-in Railway Monitoring:
- CPU usage
- Memory usage
- Network traffic
- Request count
- Error rate

### Custom Monitoring (Optional):
```python
# Add to requirements.txt
sentry-sdk==1.45.0

# Add to settings.py
import sentry_io
sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    environment='production',
)
```

---

## 🔐 Security Best Practices:

1. **Never commit `.env` to Git**
   ```bash
   # .gitignore already has:
   .env
   .env.local
   .env.*.local
   ```

2. **Use strong SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Keep DEBUG=False in production**
   ```python
   DEBUG = config('DEBUG', default=False, cast=bool)
   ```

4. **Use environment variables for secrets**
   ```python
   STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
   # NOT: STRIPE_SECRET_KEY = 'sk_live_hardcoded'  ❌
   ```

5. **Enable HTTPS (already configured)**
   ```python
   SECURE_SSL_REDIRECT = True
   ```

---

## 📝 Next Steps After Deployment:

1. **Update Frontend:**
   ```javascript
   const API_URL = 'https://your-project.up.railway.app/api';
   ```

2. **Configure Custom Domain (Optional):**
   - Railway Settings → Domains → Add Custom Domain
   - Update DNS records

3. **Set Up Monitoring:**
   - Enable Railway metrics
   - Add Sentry for error tracking

4. **Database Backups:**
   - Railway has automatic backups
   - Or use `pg_dump` for manual backups

5. **CI/CD Pipeline:**
   - Already configured via GitHub
   - Push to `main` = auto-deploy

---

## 🆘 Common Issues & Solutions:

### Issue: Build fails with "Module not found"
**Solution:** Add package to `requirements.txt`

### Issue: Static files not loading (404)
**Solution:** Run `collectstatic`
```bash
railway run python manage.py collectstatic --noinput
```

### Issue: Database migration error
**Solution:** Run migrations manually
```bash
railway run python manage.py migrate --run-syncdb
```

### Issue: WebSocket connection fails
**Solution:** Verify Daphne is running, not Gunicorn

### Issue: Celery tasks not running
**Solution:** Check Celery worker logs
```bash
railway logs --service celery-worker
```

---

## ✅ Installation Complete!

**Status:** ✅ Ready to Deploy  
**Time Required:** 5-10 minutes  
**Difficulty:** Easy  
**Cost:** $5-10/month  

**Next Action:** Follow `RAILWAY_QUICK_START.md` for deployment!

---

**Created:** $(date)  
**Python:** 3.11.8  
**Django:** 5.2.7  
**Database:** PostgreSQL  
**Platform:** Railway.app  
