# VONAGE WEBHOOK CONFIGURATION - COMPLETE API GUIDE

Based on Official Vonage API Documentation

---

## 📚 VONAGE WEBHOOK SETUP (Official Method)

### Source: https://developer.vonage.com/
### Voice API Documentation: https://developer.vonage.com/voice-api

---

## 1️⃣ WHAT IS A WEBHOOK?

A **webhook** is a callback URL that Vonage sends events to.

```
Your Phone Call
    ↓
Vonage Servers
    ↓
Send HTTP POST to your webhook URL
    ↓
Your Django Server receives and processes
    ↓
You respond with NCCO (instructions)
```

---

## 2️⃣ TWO WAYS TO SET WEBHOOKS

### Method 1: Via Vonage Dashboard (GUI)
```
Dashboard → Voice → Settings → Configure Webhooks
```

### Method 2: Via API (Programmatic)
```bash
curl -X PUT https://api.nexmo.com/v1/applications/{application-id} \
  -H "Authorization: Bearer {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Voice App",
    "voice": {
      "webhooks": {
        "answer_url": "https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/",
        "event_url": "https://your-ngrok-url/api/hume-twilio/vonage-event-callback/"
      }
    }
  }'
```

---

## 3️⃣ DASHBOARD METHOD (Easiest for You)

### Step-by-Step:

```
1. Login: https://dashboard.vonage.com/
   
2. Click: Voice (left sidebar)
   
3. Scroll Down: Find Settings
   
4. Look for: "Webhook URLs" or "Webhooks"
   
5. Find Two Fields:
   
   a) Answer Webhook
      URL: https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/
      Method: POST
   
   b) Event Webhook
      URL: https://your-ngrok-url/api/hume-twilio/vonage-event-callback/
      Method: POST
   
6. Click: SAVE or UPDATE
   
7. Done! ✅
```

---

## 4️⃣ WEBHOOK TYPES & WHAT THEY DO

### Answer Webhook (For Incoming/Starting Calls)
```
WHEN: Call connects
SENDS: {
  "from": "+1234567890",
  "to": "+15618367253",
  "uuid": "call-uuid",
  "conversation_uuid": "conv-uuid"
}
EXPECTS: NCCO response (call instructions)
YOUR_URL: /api/hume-twilio/vonage-voice-webhook/
```

### Event Webhook (For Call Events)
```
WHEN: Call answered, ringing, completed, etc.
SENDS: {
  "uuid": "call-uuid",
  "status": "answered",  // or "ringing", "completed", etc.
  "timestamp": "2025-10-30T12:00:00Z"
}
EXPECTS: 200 OK response (no content needed)
YOUR_URL: /api/hume-twilio/vonage-event-callback/
```

---

## 5️⃣ NCCO (Call Instructions)

When Vonage calls your Answer Webhook, you respond with NCCO:

```json
{
  "action": "stream",
  "streamUrl": ["wss://your-ngrok-url/ws/vonage-stream/{uuid}/"]
}
```

OR (for simple IVR):

```json
[
  {
    "action": "talk",
    "text": "Hello, connecting you now"
  },
  {
    "action": "stream",
    "streamUrl": ["wss://your-ngrok-url/ws/vonage-stream/{uuid}/"]
  }
]
```

---

## 6️⃣ VONAGE API FLOW (What Happens)

```
1. You make API call:
   POST /v1/calls
   {
     "to": [{"type": "phone", "number": "+923403471112"}],
     "from": {"type": "phone", "number": "+15618367253"},
     "ncco": [{"action": "stream", "streamUrl": [...]}]
   }
   
2. Vonage dials the number
   
3. Call connects
   
4. Vonage calls YOUR Answer Webhook:
   POST https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/
   Body: {call details}
   
5. Your server responds with NCCO (instructions)
   
6. Vonage follows NCCO instructions
   
7. During call, Vonage sends event updates:
   POST https://your-ngrok-url/api/hume-twilio/vonage-event-callback/
   Body: {"uuid": "...", "status": "ringing"}
   
8. Your server responds: {"status": "ok"}
   
9. Call ends, final event sent
   
10. WebSocket closes
```

---

## 7️⃣ YOUR CONFIGURATION (Already Done!)

### In Your Code:

**File: `vonage_voice_bridge.py`**
```python
# When making a call, sends NCCO:
ncco = [
    {
        "action": "stream",
        "streamUrl": [
            f"wss://your-ngrok-url/ws/vonage-stream/{call_uuid}/"
        ]
    }
]

call = vonage_client.voice.create_call(
    to=[{"type": "phone", "number": to_number}],
    from_={"type": "phone", "number": VONAGE_PHONE_NUMBER},
    ncco=ncco
)
```

**File: `routing.py`**
```python
# Handles incoming webhooks:
urlpatterns = [
    # Event webhook endpoint
    path('api/hume-twilio/vonage-event-callback/', 
         vonage_event_callback, 
         name='vonage-event-callback'),
    
    # WebSocket endpoint
    path('ws/vonage-stream/<uuid:uuid>/', 
         VonageRealTimeConsumer.as_asgi(),
         name='vonage-stream'),
]
```

---

## 8️⃣ WHAT YOU NEED TO DO IN DASHBOARD

### Find These Fields:

1. **Answer Webhook URL**
   ```
   https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/
   ```

2. **Event Webhook URL**
   ```
   https://your-ngrok-url/api/hume-twilio/vonage-event-callback/
   ```

3. **Method (for both)**
   ```
   POST
   ```

4. **Status**
   ```
   Active or Enabled
   ```

### Save
```
Click: Save / Update / Apply
Wait for: "Settings saved successfully"
```

---

## 9️⃣ WEBHOOK PAYLOAD EXAMPLES

### Answer Webhook Receives:
```json
{
  "from": "+1234567890",
  "to": "+15618367253",
  "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "conversation_uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": "2025-10-30T12:00:00Z"
}
```

### Your Answer Webhook Should Return:
```json
[
  {
    "action": "stream",
    "streamUrl": ["wss://your-ngrok-url/ws/vonage-stream/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/"]
  }
]
```

### Event Webhook Receives:
```json
{
  "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "answered",
  "timestamp": "2025-10-30T12:00:05Z"
}
```

### Your Event Webhook Should Return:
```
200 OK
(No body needed)
```

---

## 🔟 API ENDPOINT REFERENCE

### Create Call (What Your Code Does)
```
POST /v1/calls
Header: Authorization: Bearer {JWT}
Body: {
  "to": [{"type": "phone", "number": "+923403471112"}],
  "from": {"type": "phone", "number": "+15618367253"},
  "ncco": [{"action": "stream", "streamUrl": [...]}]
}
Response: {
  "uuid": "call-uuid",
  "status": "initiated"
}
```

### Get Call Status
```
GET /v1/calls/{call-uuid}
Response: {
  "uuid": "call-uuid",
  "status": "completed",
  "duration": 120
}
```

### Hangup Call
```
PUT /v1/calls/{call-uuid}
Body: {"action": "hangup"}
Response: {"status": "ok"}
```

---

## 1️⃣1️⃣ WEBHOOK RESPONSE REQUIREMENTS

### Answer Webhook (Inbound)
```
Status Code: 200 OK
Content-Type: application/json
Body: NCCO (JSON array)
Timeout: 5 seconds (must respond within 5s)
```

### Event Webhook (Status Updates)
```
Status Code: 200 OK
Content-Type: application/json or text/plain
Body: {"status":"ok"} or empty
Timeout: 5 seconds
```

---

## 1️⃣2️⃣ TROUBLESHOOTING WEBHOOKS

### Problem: "Webhook not responding"
```
Solution:
1. Make sure your ngrok URL is public
2. Make sure Django is running
3. Make sure URL in Dashboard matches your ngrok
4. Check firewall isn't blocking
5. Check your endpoint returns 200 OK
```

### Problem: "NCCO invalid"
```
Solution:
1. NCCO must be JSON array: [...]
2. Check "action" field is valid: "stream", "talk", etc.
3. Check all required fields present
4. Test NCCO format in Voice Playground
```

### Problem: "WebSocket not streaming"
```
Solution:
1. WebSocket URL must start with: wss://
2. URL must match route: /ws/vonage-stream/{uuid}/
3. Consumer must accept WebSocket connection
4. Check Consumer.connect() method runs
```

---

## 1️⃣3️⃣ DASHBOARD LOCATION (Different Versions)

### New Vonage Dashboard
```
Voice → Settings → Webhooks
```

### Old Vonage Dashboard
```
Voice → Applications → Select App → Settings
```

### If Not Found
```
Try Direct URL: https://dashboard.vonage.com/voice/settings
```

---

## 1️⃣4️⃣ YOUR NEXT STEPS

1. ✅ Get ngrok URL (from Terminal 2)
   ```
   https://your-random-id.ngrok-free.dev
   ```

2. ⏳ Go to Vonage Dashboard
   ```
   https://dashboard.vonage.com/
   ```

3. ⏳ Find Voice → Settings
   
4. ⏳ Fill in webhooks:
   ```
   Answer: https://your-random-id.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/
   Event: https://your-random-id.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
   ```

5. ⏳ Click Save

6. ⏳ Make test call

7. ✅ Done!

---

## SUMMARY

**Webhooks** are how Vonage communicates with your server:

- **Answer Webhook**: "A call came in, what should I do?"
  - You respond with NCCO (instructions)
  
- **Event Webhook**: "Call status changed"
  - You respond with OK (acknowledgment)

**Your system is already set up to handle both!**

Just add the URLs to the Vonage Dashboard and you're ready! 🚀

---

Based on: Vonage Voice API Official Documentation  
Generated: October 30, 2025  
Status: ✅ Ready to configure
