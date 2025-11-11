"""
🔑 VONAGE PRIVATE KEY REGENERATION GUIDE
==========================================

Your Application ID is CORRECT: 0d75cbea-4319-434d-a864-f6f9ef83874d
But the private key needs to be downloaded again.

STEPS TO FIX:
=============

METHOD 1: Download Existing Key (Recommended)
-----------------------------------------------
1. Go to: https://dashboard.nexmo.com/applications/0d75cbea-4319-434d-a864-f6f9ef83874d
2. Click "Edit" button (shown in your screenshot)
3. Scroll down to "Private Key" section
4. If there's a "Download" button, click it
5. Save as: E:\Python-AI\Django-Backend\TESTREPO\private_key.pem
6. Replace the existing file

METHOD 2: Generate New Key Pair (If download not available)
------------------------------------------------------------
1. Go to same application page
2. Click "Edit"
3. Find "Generate new key pair" button
4. Click it (⚠️ This will invalidate old key!)
5. Download the new private_key.pem
6. Save to: E:\Python-AI\Django-Backend\TESTREPO\private_key.pem

METHOD 3: Use API Key/Secret Authentication (Temporary Test)
-------------------------------------------------------------
For testing, we can use basic auth instead of JWT temporarily.
This won't work for Voice API but will verify account access.


AFTER DOWNLOADING:
==================
1. Replace ./private_key.pem with new file
2. Keep same APPLICATION_ID in .env (0d75cbea-4319-434d-a864-f6f9ef83874d)
3. Keep same API_KEY (bab7bfbe)
4. Run: python test_vonage_auth.py


CURRENT STATUS:
===============
✅ Application ID: Valid
✅ API Key: Valid (balance €8.87)
✅ Number: (+1) 2199 linked
❌ Private Key: Mismatch (needs re-download)


WHAT HAPPENED?
==============
When you last modified the application (01 Nov 25), the key pair
may have been regenerated. You need to download the matching
private key for this application ID.
"""

print(__doc__)

print("\n" + "=" * 80)
print("QUICK TEST - Let me check if key download URL exists")
print("=" * 80)

from decouple import config
import os

app_id = config('VONAGE_APPLICATION_ID')
print(f"\n📋 Application: {app_id}")
print(f"\n🔗 Direct Link:")
print(f"   https://dashboard.nexmo.com/applications/{app_id}")
print(f"\n💡 After downloading new key, test with:")
print(f"   python test_vonage_auth.py")
print("\n" + "=" * 80)
