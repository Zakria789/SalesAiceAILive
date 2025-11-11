"""
HUME AI & TWILIO WEBHOOK CONFIGURATION GUIDE
===========================================

Ye exact URLs aur settings use karni hain:
"""

# HUME AI DASHBOARD CONFIGURATION
"""
1. HumeAI Dashboard mein jakar Webhooks section:
   https://platform.hume.ai/dashboard/webhooks

2. Add New Webhook:
   - Name: "Django AI Agent Learning"
   - Webhook URL: https://yourdomain.com/agents/webhooks/hume-ai/
   - Method: POST
   - Content-Type: application/json

3. Select Events to Subscribe:
   ✅ conversation.objection_detected
   ✅ conversation.sentiment_changed  
   ✅ conversation.successful_response
   ✅ conversation.ended
   ✅ conversation.customer_engaged
   ✅ conversation.agent_response_rated

4. Authentication (Optional):
   - Header Name: Authorization
   - Header Value: Bearer your_webhook_secret_token

5. Test Configuration:
   - Use "Test Webhook" button
   - Should receive 200 OK response
"""

HUME_AI_WEBHOOK_CONFIG = {
    "webhook_url": "https://yourdomain.com/agents/webhooks/hume-ai/",
    "events": [
        "conversation.objection_detected",
        "conversation.sentiment_changed", 
        "conversation.successful_response",
        "conversation.ended",
        "conversation.customer_engaged"
    ],
    "authentication": {
        "type": "bearer_token",
        "token": "your_webhook_secret"
    }
}

# TWILIO CONSOLE CONFIGURATION  
"""
1. Twilio Console mein jakar:
   https://console.twilio.com/us1/develop/phone-numbers/manage/incoming

2. Your Phone Number select karke:
   - Voice Configuration section
   - Webhook URL: https://yourdomain.com/agents/webhooks/twilio/
   - HTTP Method: POST
   - Status Callback URL: https://yourdomain.com/agents/webhooks/twilio/status/

3. TwiML Apps configuration:
   https://console.twilio.com/us1/develop/voice/manage/twiml-apps
   
   - Voice Request URL: https://yourdomain.com/agents/webhooks/twilio/voice/
   - Voice Method: POST
   - Status Callback URL: https://yourdomain.com/agents/webhooks/twilio/status/
   - Status Callback Method: POST

4. Events to track:
   ✅ Call Initiated
   ✅ Call Answered  
   ✅ Call Completed
   ✅ Call Duration
   ✅ Recording Available
"""

TWILIO_WEBHOOK_CONFIG = {
    "voice_webhook": "https://yourdomain.com/agents/webhooks/twilio/voice/",
    "status_callback": "https://yourdomain.com/agents/webhooks/twilio/status/", 
    "method": "POST",
    "events": [
        "initiated", "ringing", "answered", 
        "completed", "busy", "no-answer"
    ]
}

# PRODUCTION DOMAIN EXAMPLES:
"""
Replace 'yourdomain.com' with your actual domain:

Production URLs:
- https://callcenter.yourdomain.com/agents/webhooks/hume-ai/
- https://api.yourdomain.com/agents/webhooks/twilio/

Development URLs (using ngrok):
- https://abc123.ngrok.io/agents/webhooks/hume-ai/  
- https://abc123.ngrok.io/agents/webhooks/twilio/
"""

# LOCAL DEVELOPMENT SETUP:
"""
1. Install ngrok:
   Download from: https://ngrok.com/download

2. Run Django server:
   python manage.py runserver 8000

3. In another terminal, run ngrok:
   ngrok http 8000

4. Copy the HTTPS URL:
   Example: https://abc123.ngrok.io

5. Use this URL in webhooks:
   HumeAI: https://abc123.ngrok.io/agents/webhooks/hume-ai/
   Twilio: https://abc123.ngrok.io/agents/webhooks/twilio/
"""

# WEBHOOK SECURITY (RECOMMENDED):
"""
Add webhook authentication in settings.py:
"""

WEBHOOK_SECURITY_SETTINGS = {
    "HUME_AI_WEBHOOK_SECRET": "your_secret_key_here",
    "TWILIO_AUTH_TOKEN": "your_twilio_auth_token",
    "WEBHOOK_TIMEOUT": 30,  # seconds
    "MAX_RETRIES": 3
}

# COMPLETE URL STRUCTURE:
WEBHOOK_URLS = {
    # HumeAI Webhooks
    "hume_ai_main": "/agents/webhooks/hume-ai/",
    "hume_ai_objection": "/agents/webhooks/hume-ai/objection/",
    "hume_ai_sentiment": "/agents/webhooks/hume-ai/sentiment/", 
    "hume_ai_success": "/agents/webhooks/hume-ai/success/",
    
    # Twilio Webhooks  
    "twilio_voice": "/agents/webhooks/twilio/voice/",
    "twilio_status": "/agents/webhooks/twilio/status/",
    "twilio_recording": "/agents/webhooks/twilio/recording/",
    
    # Manual/Testing
    "manual_trigger": "/agents/webhooks/manual-trigger/",
    "test_webhook": "/agents/webhooks/test/"
}

# STEP-BY-STEP CONFIGURATION:
"""
STEP 1: Deploy your Django app
- Use Railway, Heroku, or your preferred platform
- Get your production domain (e.g., https://myapp.railway.app)

STEP 2: Configure HumeAI
- Login to HumeAI platform
- Go to Webhooks settings
- Add: https://myapp.railway.app/agents/webhooks/hume-ai/
- Select conversation events
- Save configuration

STEP 3: Configure Twilio  
- Login to Twilio Console
- Go to Phone Numbers → Manage → Your Number
- Set Voice Webhook: https://myapp.railway.app/agents/webhooks/twilio/voice/
- Set Status Callback: https://myapp.railway.app/agents/webhooks/twilio/status/
- Save configuration

STEP 4: Test Configuration
- Make a test call
- Check Django logs for webhook calls
- Verify learning data is being saved
"""

# TESTING WEBHOOKS:
"""
Test HumeAI webhook:
curl -X POST https://yourdomain.com/agents/webhooks/hume-ai/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "customer_objection_detected",
    "conversation_id": "test_conv_123",
    "objection_text": "This is too expensive",
    "agent_response": "I understand your concern"
  }'

Test Twilio webhook:  
curl -X POST https://yourdomain.com/agents/webhooks/twilio/ \
  -d "CallStatus=completed&CallSid=test_call_123"
"""

# MONITORING WEBHOOKS:
"""
Add these to your Django admin or dashboard:

1. Webhook Success Rate
2. Failed Webhook Attempts  
3. Learning Events Processed
4. Agent Memory Updates
5. Performance Improvements

Monitor at: /admin/agents/webhooklog/
"""

print("🚀 Configuration Guide Ready!")
print("Replace 'yourdomain.com' with your actual domain")
print("Use ngrok for local development testing")
