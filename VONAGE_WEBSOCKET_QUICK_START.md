# VONAGE WEBSOCKET - QUICK SETUP

## ⚡ 5 MINUTE SETUP

### 1️⃣ START DJANGO (Terminal 1)
```bash
cd e:\Python-AI\Django-Backend\TESTREPO
.\venv\Scripts\Activate
daphne -b 0.0.0.0 -p 8002 core.asgi:application
```

### 2️⃣ START ngrok (Terminal 2)
```bash
ngrok http 8002
```
**Copy the URL** (e.g., `https://abc123.ngrok-free.dev`)

### 3️⃣ UPDATE VONAGE DASHBOARD
1. Go: https://dashboard.vonage.com/
2. Voice → Settings
3. Find "Event Webhook"
4. Paste: `https://abc123.ngrok-free.dev/api/hume-twilio/vonage-event-callback/`
5. Click Save

### 4️⃣ TEST CALL (Terminal 3)
```bash
curl -X POST http://localhost:8002/api/hume-twilio/call-initiation/ \
  -H "Content-Type: application/json" \
  -d '{"phone_no":"+923403471112","agent_id":1}'
```

### 5️⃣ DONE! ✅

---

## 📊 WEBSOCKET ARCHITECTURE

```
Customer Call → Vonage API → WebSocket Stream
                                    ↓
                          Your Django Server (Port 8002)
                                    ↓
                          VonageRealTimeConsumer
                                    ↓
                    Audio Processing + HumeAI EVI
                                    ↓
                    Emotion Detection + Response
                                    ↓
                          WebSocket Send Back
                                    ↓
                        Audio to Customer Phone
```

---

## 🔧 CONFIGURATION ALREADY DONE

| Component | Status | File |
|-----------|--------|------|
| Vonage API Key | ✅ Set in .env | `.env` |
| WebSocket Routes | ✅ Configured | `routing.py` |
| Consumer Class | ✅ Ready | `vonage_realtime_consumer.py` |
| Audio Conversion | ✅ Implemented | `vonage_realtime_consumer.py` |
| NCCO Generation | ✅ Configured | `vonage_voice_bridge.py` |
| HumeAI Integration | ✅ Ready | `vonage_realtime_consumer.py` |

---

## 📝 VONAGE DASHBOARD FIELDS

### Event Webhook URL
```
https://your-ngrok-url/api/hume-twilio/vonage-event-callback/
```

### Answer Webhook URL (Optional)
```
https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/
```

### Method
```
POST
```

---

## 🧪 TEST COMMANDS

### Check if Server Running
```bash
curl http://localhost:8002/
```

### Make Test Call
```bash
curl -X POST http://localhost:8002/api/hume-twilio/call-initiation/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_no": "+923403471112",
    "agent_id": 1,
    "customer_name": "Test Call"
  }'
```

### Expected Response
```json
{
  "success": true,
  "provider": "vonage",
  "call": {
    "call_sid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "status": "initiated"
  }
}
```

---

## 🎯 WHAT HAPPENS NEXT

When you make a call:

1. ✅ Vonage dials the number
2. ✅ WebSocket stream connects
3. ✅ Audio flows to HumeAI in real-time
4. ✅ Emotions detected every response
5. ✅ Responses sent back to caller
6. ✅ Entire conversation saved with emotions
7. ✅ Database records created

---

## ⚠️ IMPORTANT NOTES

### ngrok URL Changes Daily
- Every time you restart ngrok, you get a new URL
- **Update Vonage Dashboard each time**
- Or use ngrok paid plan for static URL

### Vonage Phone Number
- Current: `+15618367253`
- Make sure it's active in your Vonage account
- This is the "From" number for outbound calls

### HumeAI Config
- Current Config ID: `13624648-658a-49b1-81cb-a0f2e2b05de5`
- This controls the AI agent behavior
- Can be changed per call if needed

---

## ✅ CHECKLIST BEFORE FIRST CALL

- [ ] Django Daphne running
- [ ] ngrok tunnel active
- [ ] ngrok URL copied
- [ ] Vonage Dashboard webhook updated
- [ ] Vonage credentials verified
- [ ] HumeAI config verified
- [ ] Test database connection
- [ ] Make test call

---

## 🚀 YOU'RE READY!

All WebSocket configuration is already done in your code.

Just follow the 5-minute setup above and make your first call!

---

**Generated**: October 30, 2025  
**Status**: ✅ Ready to go
