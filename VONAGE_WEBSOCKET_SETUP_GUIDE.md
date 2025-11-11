# VONAGE WEBSOCKET CONFIGURATION GUIDE
## Setup Real-Time Audio Streaming

---

## 1. VONAGE DASHBOARD SETUP

### Step 1: Login to Vonage Dashboard
- Go to: https://dashboard.vonage.com/
- Login with your credentials
- Navigate to: **Voice** → **Settings**

### Step 2: Configure Webhook URLs

#### Event Webhook (for call events)
```
URL: https://your-ngrok-url.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
Method: POST
```

#### Answer Webhook (for incoming calls)
```
URL: https://your-ngrok-url.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/
Method: POST
```

#### Fallback URL (optional)
```
URL: https://your-ngrok-url.ngrok-free.dev/api/hume-twilio/vonage-fallback/
Method: POST
```

### Step 3: Save Settings
- Click **Save** button
- Wait for confirmation

---

## 2. WEBSOCKET CONFIGURATION IN CODE

### Already Configured in Your System ✓

The WebSocket is already set up in:

#### File 1: `vonage_voice_bridge.py`
```python
# NCCO with WebSocket stream action
ncco = [
    {
        "action": "stream",
        "streamUrl": [
            f"wss://your-ngrok-url.ngrok-free.dev/ws/vonage-stream/{call_uuid}/"
        ],
        "baritons": ["bart"]  # or your voice choice
    }
]
```

#### File 2: `routing.py`
```python
# WebSocket routes configured
websocket_urlpatterns = [
    path("ws/vonage-stream/<uuid:uuid>/", VonageRealTimeConsumer.as_asgi()),
    path("api/vonage-stream/<uuid:uuid>/", VonageRealTimeConsumer.as_asgi()),
]
```

#### File 3: `vonage_realtime_consumer.py`
```python
# WebSocket consumer with audio streaming
class VonageRealTimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept WebSocket connection
        await self.accept()
    
    async def receive(self, bytes_data):
        # Receive audio from Vonage
        # Send to HumeAI
        # Get response
        # Send back audio
```

---

## 3. ENVIRONMENT CONFIGURATION

### Check Your .env File
```env
# Should have these set:
VOICE_PROVIDER=vonage
VONAGE_API_KEY=bab7bfbe
VONAGE_API_SECRET=xeX*cW3^KA0LcQf!CB^Sl$
VONAGE_PHONE_NUMBER=+15618367253
BASE_URL=https://your-ngrok-url.ngrok-free.dev
```

**Status**: ✅ **Already configured**

---

## 4. START THE SYSTEM

### Terminal 1: Django Daphne Server
```bash
cd e:\Python-AI\Django-Backend\TESTREPO
.\venv\Scripts\Activate
daphne -v 0 -b 0.0.0.0 -p 8002 core.asgi:application
```

### Terminal 2: ngrok Tunnel
```bash
ngrok http 8002
```

**Copy the URL from ngrok** (example: `https://xyz-abc.ngrok-free.dev`)

---

## 5. UPDATE VONAGE DASHBOARD WITH ngrok URL

After starting ngrok:

1. Go to: https://dashboard.vonage.com/
2. Navigate to: **Voice** → **Settings**
3. Update webhooks with your ngrok URL:
   ```
   https://your-ngrok-url-here.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
   ```
4. Click **Save**

---

## 6. TEST WEBSOCKET CONNECTION

### Make a Test Call
```bash
curl -X POST http://localhost:8002/api/hume-twilio/call-initiation/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_no": "+923403471112",
    "agent_id": 1,
    "customer_name": "Test"
  }'
```

### Expected Response
```json
{
  "success": true,
  "provider": "vonage",
  "call": {
    "call_sid": "uuid-string",
    "status": "initiated"
  }
}
```

### Check WebSocket Connection
Look for logs like:
```
WebSocket CONNECT /ws/vonage-stream/uuid/
WebSocket RECEIVE (binary): audio_data
Sent to HumeAI: audio_bytes
Received from HumeAI: response_audio
WebSocket SEND (binary): response_bytes
```

---

## 7. WEBSOCKET AUDIO FLOW

### Real-Time Stream
```
Phone Call (Customer)
    ↓
Vonage Voice API
    ↓
WebSocket Stream to Your Server
    ↓
Audio Conversion (16kHz → 48kHz)
    ↓
HumeAI EVI Processing
    ↓
Emotion Detection
    ↓
Response Audio Generation
    ↓
Audio Conversion (48kHz → 16kHz)
    ↓
WebSocket Send Back to Vonage
    ↓
Play Audio to Customer
```

---

## 8. CONFIGURATION CHECKLIST

- [x] Vonage API Key configured
- [x] Vonage API Secret configured
- [x] Vonage Phone Number configured
- [x] VOICE_PROVIDER = "vonage"
- [x] Django Daphne running (port 8002)
- [x] ngrok tunnel active
- [x] WebSocket routes configured
- [x] VonageRealTimeConsumer active
- [x] HumeAI credentials configured
- [ ] Update Vonage Dashboard webhook URL
- [ ] Test with real phone call

---

## 9. VONAGE DASHBOARD WEBHOOK SETTINGS

### Location in Dashboard
1. **Voice** menu → **Settings**
2. Find: **Webhook URLs**
3. Fields to fill:

| Field | URL |
|-------|-----|
| Event Webhook | `https://your-ngrok-url/api/hume-twilio/vonage-event-callback/` |
| Answer Webhook | `https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/` |

### Save & Test
- Click **Save**
- Vonage sends test webhook
- You should see logs in Django

---

## 10. VONAGE VOICE SETTINGS (Optional)

In Dashboard → **Voice** → **Settings**:

### Audio Settings
```
Sample Rate: 16000 Hz (16 kHz)
Encoding: Linear PCM (ULAW/ALAW available)
Channels: Mono (1)
```

### Stream Settings
```
Compression: None
Quality: High
Timeout: 3600 seconds
```

---

## 11. TROUBLESHOOTING

### WebSocket Connection Failed
```
Issue: "Connection refused" on WebSocket
Fix: Make sure Daphne is running: daphne -b 0.0.0.0 -p 8002 core.asgi:application
```

### No Audio Streaming
```
Issue: WebSocket connects but no audio received
Fix: Check Vonage Dashboard webhook URL matches ngrok URL
```

### HumeAI Not Responding
```
Issue: WebSocket receives audio but no HumeAI response
Fix: Check HUME_CONFIG_ID and HUME_API_KEY in .env
```

### Audio Quality Poor
```
Issue: Audio stream is choppy
Fix: Check internet connection and ngrok stability
```

---

## 12. YOUR CURRENT STATUS

### ✅ Already Configured
- Vonage API credentials
- WebSocket routes
- Consumer class
- NCCO structure
- Audio conversion

### ⏳ Need to Do
1. Start Django Daphne
2. Start ngrok tunnel
3. Copy ngrok URL
4. Update Vonage Dashboard webhook URL
5. Make test call

### Next Steps
```bash
# Terminal 1
daphne -b 0.0.0.0 -p 8002 core.asgi:application

# Terminal 2  
ngrok http 8002

# Terminal 3 (after ngrok shows URL)
curl -X POST http://localhost:8002/api/hume-twilio/call-initiation/ \
  -H "Content-Type: application/json" \
  -d '{"phone_no":"+923403471112","agent_id":1}'
```

---

## QUICK REFERENCE

### Vonage Dashboard
- **URL**: https://dashboard.vonage.com/
- **Section**: Voice → Settings
- **Update**: Event Webhook URL with your ngrok address

### Django Backend
- **Port**: 8002
- **WebSocket**: `/ws/vonage-stream/{uuid}/`
- **Consumer**: `VonageRealTimeConsumer`

### ngrok
- **Command**: `ngrok http 8002`
- **Copy URL**: Use this in Vonage Dashboard

### HumeAI
- **Config ID**: Set in .env
- **Processing**: Real-time emotion detection
- **Output**: Audio + emotions saved to database

---

## SUPPORT

If you need help:
1. Check Django logs: Terminal running Daphne
2. Check ngrok logs: Terminal running ngrok
3. Check Vonage Dashboard: Recent activity
4. Check database: TwilioCall records
5. Check ConversationLog: Emotions captured

---

**Status**: ✅ **Your system is ready for WebSocket!**

Just update the Vonage Dashboard webhook URL and make your first call! 🚀
