# VONAGE VOICE SETTINGS - COMPLETE GUIDE

## 🔍 WHERE TO FIND VOICE SETTINGS

### Location in Vonage Dashboard

1. **Login**: https://dashboard.vonage.com/
2. **Click**: Left sidebar → **Voice**
3. **Select**: **Settings** (not "Applications")

---

## ⚙️ VOICE SETTINGS YOU'LL SEE

### Section 1: Webhook URLs
```
Event Webhook
├─ URL: https://your-ngrok-url/api/hume-twilio/vonage-event-callback/
├─ Method: POST
└─ Status: Active

Answer Webhook  
├─ URL: https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/
├─ Method: POST
└─ Status: Active (Optional)

Fallback Webhook
├─ URL: https://your-ngrok-url/api/hume-twilio/vonage-fallback/
├─ Method: POST
└─ Status: Inactive (Optional)
```

### Section 2: Inbound Calling
```
Inbound Calling: ON/OFF
├─ If ON: Can receive calls via Vonage
├─ If OFF: Only outbound calls work
└─ Status: Recommended ON for 2-way calls
```

### Section 3: Premium Routing
```
Premium Routing: ON/OFF
├─ Better call quality
├─ Lower latency
└─ Recommended: ON
```

### Section 4: Default Number
```
Default Number: Select your main number
├─ This is used for outbound calls
├─ Current: +15618367253 (from your .env)
└─ Can set fallback number
```

---

## 🎯 SETTINGS YOU NEED FOR VONAGE + HUMEAI

### Must Have ✅
1. **Event Webhook**: Set and active
2. **Answer Webhook**: Set and active (for incoming calls)
3. **Inbound Calling**: Enabled (if you want to receive calls)
4. **Number Selected**: Your Vonage number

### Optional 📋
1. Premium Routing: Recommended
2. Fallback Webhook: For redundancy
3. Default Call Handler: Advanced

---

## 📸 WHAT YOU SHOULD SEE

```
Voice
├── Settings
│   ├── ✅ Event Webhook Configured
│   ├── ✅ Answer Webhook Configured  
│   ├── ✅ Inbound Calling: ON
│   ├── ✅ Number: +15618367253
│   ├── ✅ Status: Active
│   └── ✅ Save button
│
├── Applications
│   └── Your voice app
│
├── Numbers
│   ├── +15618367253 (Your number)
│   └── Status: Active
│
└── Logs
    └── Recent webhook calls
```

---

## 🔧 STEP-BY-STEP SETUP

### Step 1: Navigate to Voice Settings
```
Dashboard → Voice (left menu) → Settings
```

### Step 2: Fill Event Webhook
```
Field: Event Webhook URL
Value: https://your-ngrok-url/api/hume-twilio/vonage-event-callback/
Method: POST
✓ Check "Active"
```

### Step 3: Fill Answer Webhook (Optional but Recommended)
```
Field: Answer Webhook URL  
Value: https://your-ngrok-url/api/hume-twilio/vonage-voice-webhook/
Method: POST
✓ Check "Active"
```

### Step 4: Enable Inbound Calling
```
Inbound Calling: Toggle ON
(Only if you want to receive calls)
```

### Step 5: Select Default Number
```
Default Number: +15618367253 (your Vonage number)
```

### Step 6: Save
```
Click: SAVE button (bottom right)
Wait for: "Settings saved successfully"
```

### Step 7: Test
```
Check: Recent webhook calls in Logs
Make test call to verify
```

---

## 🧪 HOW TO TEST WEBHOOKS

### From Vonage Dashboard

1. **Voice** → **Settings**
2. Find: **Event Webhook**
3. Click: **Test Webhook** (if available)
4. Should see: Success message

### From Your Backend

```bash
# Check Django logs
tail -f logs/django.log

# Should see:
# Webhook received from Vonage
# Call event processed
# Audio stream connected
```

---

## ⚠️ COMMON ISSUES & FIXES

### Issue 1: "Webhook URL not responding"
```
Problem: Vonage tries to send webhook but gets no response
Fix:
1. Make sure Django is running (daphne -b 0.0.0.0 -p 8002)
2. Make sure ngrok is running
3. Make sure URL in Vonage matches your ngrok URL
4. Check firewall/network
```

### Issue 2: "ngrok URL changed but forgot to update"
```
Problem: Webhooks not working after restarting ngrok
Fix:
1. Copy new URL from ngrok
2. Go to Vonage Dashboard
3. Update Event Webhook URL
4. Click Save
5. Test again
```

### Issue 3: "Can't receive calls"
```
Problem: Inbound calling not working
Fix:
1. Make sure "Inbound Calling" is ON in Settings
2. Answer Webhook should be set
3. Number should be active
4. ngrok URL should be correct
```

### Issue 4: "WebSocket not connecting"
```
Problem: Real-time audio stream fails
Fix:
1. WebSocket route should be: /ws/vonage-stream/{uuid}/
2. Check Django routing.py has WebSocket routes
3. Make sure Daphne is running (not Django development server)
4. Check for SSL/TLS issues if using HTTPS
```

---

## 📊 COMPARISON: SETTINGS FOR DIFFERENT SCENARIOS

### Scenario 1: Outbound Calls Only
```
Event Webhook: ✅ Required
Answer Webhook: ❌ Not needed
Inbound Calling: ❌ OFF
Default Number: ✅ Required
```

### Scenario 2: 2-Way Conversation (Your Setup)
```
Event Webhook: ✅ Required
Answer Webhook: ✅ Recommended
Inbound Calling: ✅ ON (if needed)
Default Number: ✅ Required
```

### Scenario 3: WebSocket Real-Time
```
Event Webhook: ✅ Required
Answer Webhook: ✅ Required (for real-time)
Inbound Calling: ✅ ON (for incoming)
Default Number: ✅ Required
WebSocket Stream: ✅ In NCCO
```

---

## 🎛️ ADVANCED SETTINGS (Optional)

### If You See These, Here's What They Mean:

```
Conference Enabled
├─ Allows multiple people in call
└─ Not needed for 1-on-1 calls

Recording Enabled
├─ Automatically records calls
└─ May need compliance notice

Premium Routing
├─ Better quality connections
└─ Recommended: ON

Fallback Number
├─ If primary fails, call this
└─ Optional

Default Call Handler
├─ What to do with unknown calls
└─ Usually leave as is
```

---

## ✅ YOUR CURRENT STATUS

Based on your .env file:

```
✅ VONAGE_API_KEY: bab7bfbe (Set)
✅ VONAGE_API_SECRET: xeX*cW3^... (Set)
✅ VONAGE_PHONE_NUMBER: +15618367253 (Set)
✅ VOICE_PROVIDER: vonage (Set)
✅ BASE_URL: https://your-ngrok-url (Set)

⏳ Still Need To Do:
   1. Update Vonage Dashboard webhook URL
   2. Enable Event Webhook
   3. Optional: Enable Answer Webhook for 2-way
   4. Optional: Enable Inbound Calling
   5. Test webhook connection
```

---

## 🚀 QUICK CHECKLIST

- [ ] Go to https://dashboard.vonage.com/
- [ ] Navigate to Voice → Settings
- [ ] Copy your ngrok URL
- [ ] Paste in Event Webhook field
- [ ] Set Method to POST
- [ ] Enable Inbound Calling (optional)
- [ ] Click Save
- [ ] See "Settings saved" message
- [ ] Test webhook
- [ ] Make test call

---

## 📞 WHAT HAPPENS AFTER YOU SAVE

```
1. Vonage saves your webhook URLs
2. System ready to receive events
3. Next incoming/outgoing call:
   - Event Webhook fires
   - Your Django receives it
   - WebSocket stream starts
   - Real-time audio begins
   - HumeAI processes speech
   - Response sent back
   - Emotions captured
   - Database updated
```

---

## 🎓 VOICE SETTINGS EXPLAINED

| Setting | What It Does | Your Setup |
|---------|-------------|-----------|
| Event Webhook | Sends call events to your server | ✅ Set to Daphne server |
| Answer Webhook | Sends call started event | ✅ Set to Daphne server |
| Inbound Calling | Can receive calls | ⏳ Optional (enable if needed) |
| Default Number | Outbound call "from" number | ✅ +15618367253 |
| Premium Routing | Better call quality | ⏳ Optional (recommended ON) |
| Fallback Webhook | Backup if primary fails | ❌ Not needed |

---

## 🔐 SECURITY NOTE

Your Event Webhook URL should:
- ✅ Be HTTPS (Vonage requires it)
- ✅ Have valid SSL certificate (ngrok provides this)
- ✅ Be publicly accessible (ngrok tunnels your local server)
- ✅ Accept POST requests
- ✅ Respond within 5 seconds
- ❌ Don't expose API keys in URL

---

## 📝 SUMMARY

**Voice Settings** in Vonage Dashboard is where you:
1. Configure webhook URLs (where Vonage sends events)
2. Enable/disable features
3. Set default numbers
4. Test connections
5. Monitor logs

**Your next step**: Update the Event Webhook URL with your ngrok address!

---

Generated: October 30, 2025  
Status: ✅ Ready to configure
