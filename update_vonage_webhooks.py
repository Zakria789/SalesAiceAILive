"""
Update Vonage Application Webhook URLs
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from decouple import config
import requests

print("=" * 80)
print("VONAGE WEBHOOK URLS UPDATE")
print("=" * 80)

api_key = config('VONAGE_API_KEY')
api_secret = config('VONAGE_API_SECRET')
app_id = config('VONAGE_APPLICATION_ID')
base_url = config('BASE_URL')

print(f"\n📋 Current Configuration:")
print(f"   Application ID: {app_id}")
print(f"   Base URL: {base_url}")

# Correct webhook URLs for OUTGOING calls
answer_url = f"{base_url}/api/hume-twilio/vonage-outgoing-answer/"
event_url = f"{base_url}/api/hume-twilio/vonage-event-callback/"

print(f"\n🔗 New Webhook URLs (for OUTGOING calls):")
print(f"   Answer: {answer_url}")
print(f"   Event: {event_url}")

# Get current application
url = f"https://api.nexmo.com/v2/applications/{app_id}"
response = requests.get(url, auth=(api_key, api_secret))

if response.status_code == 200:
    app_data = response.json()
    
    print(f"\n✅ Application found: {app_data.get('name')}")
    
    # Update webhooks
    capabilities = app_data.get('capabilities', {})
    
    # Update voice webhooks
    if 'voice' not in capabilities:
        capabilities['voice'] = {}
    
    capabilities['voice']['webhooks'] = {
        'answer_url': {
            'address': answer_url,
            'http_method': 'POST'
        },
        'event_url': {
            'address': event_url,
            'http_method': 'POST'
        }
    }
    
    # Prepare update payload
    update_payload = {
        'name': app_data.get('name'),
        'capabilities': capabilities
    }
    
    print(f"\n🔧 Updating application...")
    update_response = requests.put(
        url,
        auth=(api_key, api_secret),
        headers={'Content-Type': 'application/json'},
        json=update_payload
    )
    
    if update_response.status_code == 200:
        print(f"✅ WEBHOOK URLS UPDATED!")
        print(f"\n🎉 Vonage will now call:")
        print(f"   {answer_url}")
        print(f"   when calls are answered!")
    else:
        print(f"❌ Update failed: {update_response.status_code}")
        print(f"   {update_response.text}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(f"   {response.text}")

print(f"\n" + "=" * 80)
