#!/bin/bash
# 🔐 Run this script to create admin user on Railway after deployment

echo "🚀 Creating admin user on Railway production..."

# Option 1: Using Railway CLI (recommended)
echo "Running: railway run python manage.py createadmin"
railway run python manage.py createadmin

echo "✅ Admin user creation completed!"
echo "🌐 Access admin at: https://salesaiceailive-production.up.railway.app/admin/"
echo "👤 Username: admin"
echo "📧 Email: SalesAice.ai@gmail.com"
echo "🔑 Password: Aiceinthehole"