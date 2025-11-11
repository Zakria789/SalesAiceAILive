#!/usr/bin/env python
"""
🔍 VONAGE WEBHOOK DEBUG
Check what webhooks Vonage is actually sending
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    VONAGE WEBHOOK DEBUG ANALYSIS                           ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 SERVER LOGS ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

From the logs you showed:

[16:07:52] ✅ Vonage Event Callback: answered
           UUID: c17dc76c-1628-47da-9621-b78e5cacf340
           
[16:08:12] ✅ Vonage Event Callback: answered (again)
           UUID: c17dc76c-1628-47da-9621-b78e5cacf340

[16:08:13] ❌ 404 - /api/hume-twilio/vonage-fallback/
           This endpoint doesn't exist!

[16:08:13] ✅ Vonage Event Callback: completed
           UUID: c17dc76c-1628-47da-9621-b78e5cacf340


❌ THE PROBLEM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The answer_url webhook was NEVER called!

Why?
────
1. Vonage is calling event_callback (answered)
   BUT NOT calling answer_url webhook

2. answer_url should be called FIRST to get NCCO instructions
   Then event_callback is called for status updates

3. Instead:
   - answer_url: ❌ NOT CALLED
   - event_callback: ✅ CALLED (but too late!)

Result:
   - No WebSocket stream setup ❌
   - No HumeAI connection ❌
   - No voice response ❌
   - Call disconnected immediately ❌


🔧 ROOT CAUSE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Vonage Voice Application Configuration Issue!

The NCCO (call flow) is not being requested properly.

In vonage_sdk_call.py, we're specifying:
   - answer_url: https://ngrok-url/api/hume-twilio/vonage-voice-webhook/
   - event_url: https://ngrok-url/api/hume-twilio/vonage-event-callback/

But Vonage might not be calling answer_url because:

POSSIBLE CAUSES:
1. Answer URL not in Vonage Application config
2. Event URL being used instead of Answer URL
3. Webhook timing issue
4. Vonage API version mismatch


✅ SOLUTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1: Update Vonage Application Dashboard
────────────────────────────────────────────

Log in to Vonage Dashboard:
1. Go to: https://dashboard.vonage.com/applications
2. Select your Voice Application: 0d75cbea-4319-434d-a864-f6f9ef83874d
3. Under "Capabilities" → "Voice":
   ✅ Answer URL: https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/
   ✅ Event URL: https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
4. Click "Save"

Option 2: Handle in event_callback (Quick Fix)
───────────────────────────────────────────────

Modify vonage_event_callback to handle WebSocket setup:

When event = 'answered':
   1. Create TwilioCall record
   2. Return NCCO with stream action
   3. This will start WebSocket immediately

This would bypass the need for separate answer_url webhook.


🎯 WHAT NEEDS TO HAPPEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Correct Call Flow:

[1] vonage_sdk_call.py makes call
        ↓
[2] Vonage connects to phone
        ↓
[3] Vonage calls: answer_url webhook ← THIS MUST HAPPEN!
        ├─ Receives NCCO with stream action
        └─ Opens WebSocket connection
        ↓
[4] Phone connects to WebSocket
        ├─ VonageRealTimeConsumer accepts
        └─ Connects to HumeAI
        ↓
[5] Real-time conversation starts
        ├─ Audio exchange
        ├─ Emotion detection
        └─ Voice responses
        ↓
[6] Vonage calls: event_callback (completed)
        └─ Call ends


🔴 CURRENT FLOW (BROKEN):

[1] vonage_sdk_call.py makes call
        ↓
[2] Vonage connects to phone
        ↓
[3] Vonage calls: event_callback (answered) ← SKIPS answer_url!
        └─ No NCCO instructions received
        └─ No WebSocket stream started
        ↓
[4] Call disconnects (no instructions)
        ↓
[5] Vonage calls: event_callback (completed)
        └─ Too late - call already ended!


🛠️ QUICK FIX - Handle "answered" in event_callback:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instead of returning 404, respond with NCCO when "answered" event received.

In vonage_event_callback, add:

if event == 'answered':
    # Create call record
    # Return NCCO with stream action
    # This will trigger WebSocket connection
    return JsonResponse(ncco, safe=False)

This makes event_callback do what answer_url should do.


📋 ACTION NEEDED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Choose one:

BEST: Update Vonage Dashboard (proper setup)
   - Requires manual configuration
   - Most reliable long-term

QUICK: Modify vonage_event_callback
   - Handles "answered" event in same webhook
   - Works immediately
   - Still effective

Which would you like? 1 or 2?
""")
