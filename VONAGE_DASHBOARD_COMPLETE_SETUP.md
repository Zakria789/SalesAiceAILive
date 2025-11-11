# VONAGE DASHBOARD - COMPLETE SETUP GUIDE

## YOUR CREDENTIALS (Already in .env)

```
VONAGE_API_KEY:      bab7bfbe
VONAGE_API_SECRET:   xeX*cW3^KA0LcQf!CB^Sl$
VONAGE_PHONE_NUMBER: +15618367253
ngrok BASE_URL:      https://uncontortioned-na-ponderously.ngrok-free.dev
```

---

## ⚠️ IMPORTANT NOTES

### ngrok URL Changes Daily
- **Your current URL**: `https://uncontortioned-na-ponderously.ngrok-free.dev`
- Every time you restart ngrok, you get a NEW URL
- When URL changes, you must UPDATE it in Vonage Dashboard

### API Key & Secret
- **Don't need to add these to Vonage Dashboard**
- These are for YOUR code to call Vonage (already configured)
- Vonage Dashboard just needs the webhook URLs

---

## 🎯 STEP-BY-STEP VONAGE DASHBOARD SETUP

### STEP 1: Login to Vonage
```
Go to: https://dashboard.vonage.com/
Login with your credentials
```

### STEP 2: Navigate to Voice Settings
```
Left Menu → Voice
         ↓
Scroll Down
         ↓
Settings (or click direct link below)
```

**Direct Link**: https://dashboard.vonage.com/voice/settings

### STEP 3: Find "Webhooks" Section
```
Look for:
├─ Event Webhook URL
├─ Answer Webhook URL
└─ Inbound Calling
```

---

## 📝 WEBHOOK CONFIGURATION

### Webhook 1: Event Webhook (MUST HAVE)

**Field**: Event Webhook URL  
**Value**:
```
https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
```

**Method**: POST  
**Status**: Active ✓

---

### Webhook 2: Answer Webhook (For Incoming Calls)

**Field**: Answer Webhook URL  
**Value**:
```
https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/
```

**Method**: POST  
**Status**: Active ✓

---

## ⚙️ OTHER SETTINGS

### Inbound Calling (Optional)
```
Enable: ON or OFF (depends on if you want to RECEIVE calls)
If OFF: Only OUTBOUND calls work (calling others)
If ON: Both INBOUND and OUTBOUND work
```

### Default Number
```
Select: +15618367253 (your Vonage number)
This is the "FROM" number for outbound calls
```

---

## 🔐 API KEY & SECRET (Already Configured)

### IMPORTANT: Where to Get/Verify Them

These are **NOT added in Dashboard Settings**. They're used in YOUR CODE:

```
Vonage Dashboard → Account → Settings → API Credentials

Your Current Credentials:
├─ API Key:    bab7bfbe
└─ API Secret: xeX*cW3^KA0LcQf!CB^Sl$
```

**To Verify They're Correct**:

1. Go to: https://dashboard.vonage.com/settings/api-credentials
2. Find: "API Key" and "API Secret"
3. Compare with your .env file
4. If different, update .env with correct ones

---

## ✅ COMPLETE VONAGE SETUP CHECKLIST

### In Vonage Dashboard:

- [ ] **Event Webhook URL**: 
  ```
  https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
  ```

- [ ] **Answer Webhook URL**: 
  ```
  https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/
  ```

- [ ] **Method** (both): `POST`

- [ ] **Status** (both): `Active`

- [ ] **Default Number**: `+15618367253`

- [ ] **Save/Update** button clicked

- [ ] **Confirmation message** appeared

---

## 🧪 TEST YOUR SETUP

### After Configuring Webhooks:

```
1. Go to Vonage Dashboard
2. Voice → Logs or Recent Activity
3. Make a test call from your code
4. Check if webhooks are being called
5. Look for green checkmarks or success messages
```

---

## 📊 WEBHOOK URL BREAKDOWN

Your event webhook URL:
```
https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
│        │                                           │
│        │                                           └─ Endpoint (where to send)
│        │
│        └─ ngrok public URL (tunnels to your local Django)
│
└─ HTTPS required (secure)
```

---

## 🚨 COMMON MISTAKES TO AVOID

### ❌ DON'T DO:
```
1. Don't paste API key/secret in Dashboard webhook field
   (They go in your .env file, not Dashboard)

2. Don't forget to click SAVE button
   (Changes won't apply without saving)

3. Don't use old ngrok URL after restarting
   (Update when you get new URL)

4. Don't forget trailing slash
   (Use: /vonage-event-callback/  NOT  /vonage-event-callback)

5. Don't use HTTP
   (Must be HTTPS)
```

### ✅ DO:
```
1. Use your ngrok URL
2. Click SAVE after changes
3. Update URL if ngrok restarts
4. Include trailing slashes
5. Use HTTPS
6. Keep POST method
```

---

## 🔄 IF ngrok URL CHANGES

### When ngrok restarts, you get a new URL:

**Old**: https://abc123.ngrok-free.dev/...  
**New**: https://xyz789.ngrok-free.dev/...

### What to do:

1. Stop your server (if needed)
2. Restart ngrok
3. Copy new URL
4. Go to Vonage Dashboard
5. Update Event Webhook URL with new URL
6. Update Answer Webhook URL with new URL
7. Click SAVE
8. Test again

---

## 📞 YOUR API CREDENTIALS LOCATION

To verify or update your Vonage credentials:

```
Vonage Dashboard
└─ Account (top right menu)
   └─ Settings
      └─ API Credentials
         ├─ API Key
         └─ API Secret
```

**Your current credentials in .env**:
```
API Key:    bab7bfbe
API Secret: xeX*cW3^KA0LcQf!CB^Sl$
```

---

## 🎯 WHAT HAPPENS AFTER YOU SAVE

```
1. Vonage saves your webhook URLs

2. System ready to handle calls

3. When you make a call:
   └─ Event Webhook is called (status update)
      └─ Your Django receives it
      └─ Processes and responds

4. When WebSocket connects:
   └─ Real-time audio streaming begins
   └─ HumeAI processes speech
   └─ Emotions captured
   └─ Response sent back

5. Call ends:
   └─ Final event webhook called
   └─ Call saved to database
```

---

## 📋 COMPLETE CONFIGURATION SUMMARY

### Your Setup:

| Component | Value | Status |
|-----------|-------|--------|
| Provider | vonage | ✅ Set |
| API Key | bab7bfbe | ✅ Set |
| API Secret | xeX*cW3^KA0LcQf!CB^Sl$ | ✅ Set |
| Phone Number | +15618367253 | ✅ Set |
| Event Webhook | https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-event-callback/ | ⏳ Add to Dashboard |
| Answer Webhook | https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/ | ⏳ Add to Dashboard |
| ngrok URL | https://uncontortioned-na-ponderously.ngrok-free.dev | ✅ Active |

---

## 🚀 NEXT STEPS

1. **Open Vonage Dashboard**: https://dashboard.vonage.com/
2. **Go to Voice Settings**: Voice → Settings
3. **Add Event Webhook**: Copy-paste the URL above
4. **Add Answer Webhook**: Copy-paste the URL above
5. **Click Save**
6. **Test**: Make a call and check logs
7. **Done!** ✅

---

## 💬 SUMMARY

You have:
- ✅ Vonage API key
- ✅ Vonage API secret
- ✅ Your phone number
- ✅ ngrok URL (tunnel)
- ✅ Django endpoints ready

You just need to:
- ⏳ Add webhook URLs to Vonage Dashboard
- ⏳ Click Save
- ⏳ Test!

**Everything else is already configured!** 🎉

---

Generated: October 30, 2025  
Status: ✅ Ready to add to Vonage Dashboard
