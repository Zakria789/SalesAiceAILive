# 🚀 Railway Deployment - Quick Start (5 Minutes)

## Sirf 5 Steps Me Deploy Karo! 🎯

---

## ✅ STEP 1: Railway Account (30 seconds)

```
1. https://railway.app pe jao
2. "Start a New Project" → "Deploy from GitHub repo"
3. GitHub se login karo
4. TESTREPO repository select karo
```

✅ **Done!** Railway code pull kar lega.

---

## ✅ STEP 2: Database Add Karo (30 seconds)

```
1. Project dashboard pe "New" button click
2. "Database" → "Add PostgreSQL"
3. Wait for provisioning (10 seconds)
```

✅ **Done!** DATABASE_URL automatically set ho gaya.

---

## ✅ STEP 3: Environment Variables (2 minutes)

Project settings → "Variables" tab → Add these:

```bash
SECRET_KEY=django-insecure-your-secret-key-change-this-now
DEBUG=False
RAILWAY_ENVIRONMENT=production

# Copy from your .env file:
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890

HUME_API_KEY=xxxxx
HUME_SECRET_KEY=xxxxx

STRIPE_SECRET_KEY=sk_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_xxxxx
```

✅ **Done!** Variables saved.

---

## ✅ STEP 4: Deploy! (2 minutes)

```
Railway automatically:
1. ✅ Builds app (pip install)
2. ✅ Collects static files
3. ✅ Runs migrations
4. ✅ Starts server
```

**Watch live logs:**
- Deployments tab → Latest deployment → View logs

✅ **Done!** App live ho gaya! 🎉

---

## ✅ STEP 5: Get Your URL (10 seconds)

```
1. Settings → "Domains"
2. Copy URL: https://your-project.up.railway.app
3. Test: https://your-project.up.railway.app/admin/
```

✅ **Done!** App deployed! 🚀

---

## 🔧 Optional: Add Redis + Celery (1 minute)

```
1. "New" → "Database" → "Add Redis"
2. "New" → "Empty Service" → Name: celery-worker
   Start Command: celery -A core worker --loglevel=info
3. "New" → "Empty Service" → Name: celery-beat
   Start Command: celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

✅ **Done!** Background tasks working!

---

## 📝 Create Superuser

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login & link project
railway login
railway link

# Create superuser
railway run python manage.py createsuperuser
```

---

## 🎉 Success Checklist

- [ ] App deployed to Railway
- [ ] PostgreSQL connected
- [ ] Environment variables set
- [ ] Admin panel accessible
- [ ] API working
- [ ] Superuser created

---

## 🚨 Common Issues

### Build Failed?
```
Check: Deployments → Logs
Fix: Missing environment variable
```

### Static files not loading?
```
Railway run: python manage.py collectstatic --noinput
```

### Database error?
```
Railway run: python manage.py migrate
```

---

## 📞 Need Help?

**Full Guide:** `RAILWAY_DEPLOYMENT_GUIDE.md`

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

---

**Total Time:** 5 minutes ⏱️
**Cost:** Free ($5/month credit) 💰
**Difficulty:** Easy 🟢
**Status:** ✅ Production Ready
