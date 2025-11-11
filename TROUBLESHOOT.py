#!/usr/bin/env python
"""
🔧 QUICK TROUBLESHOOTING GUIDE
What to check if second call doesn't work
"""

troubleshooting_steps = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    TROUBLESHOOTING SECOND CALL                             ║
╚════════════════════════════════════════════════════════════════════════════╝

📞 CALL STATUS: RINGING
UUID: f304eb6f-5dc8-48ef-a322-38cd1546a8ef
To: +923403471112


🚨 ISSUE #1: Phone rings but no sound from agent (just silence)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symptom: Connected but no voice / one-way audio

Likely cause: HumeAI not connected or not responding

Steps:
1. Check Django logs for:
   ✅ Should see: "ANSWERED event detected - Setting up WebSocket stream"
   ✅ Should see: "Vonage WebSocket connection established"
   ✅ Should see: "Connected to HumeAI EVI"
   
   ❌ If missing: HumeAI connection failed

2. Run HumeAI diagnostic:
   > python debug_hume_voice.py
   
   If test fails:
   - Check HUME_API_KEY in .env
   - Check HUME_CONFIG_ID in .env
   - Verify endpoint: wss://api.hume.ai/v0/assistant/chat?config_id=...

3. Check WebSocket connection:
   Look for: "🔗 Vonage WebSocket connection established"
   If not present:
   - Check ngrok tunnel is active
   - Check Django server running on port 8002
   - Check WEBSOCKET_ACCEPT_ALL = True in settings


🚨 ISSUE #2: Call answers but immediately disconnects (5 second call)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symptom: Connection dropped, no stream established

Likely cause: NCCO not returned from event_callback

Steps:
1. Check Django logs for:
   ✅ Should see: "ANSWERED event detected"
   ✅ Should see: "Returning NCCO stream setup"
   
   ❌ If not present: Fix not applied correctly

2. Verify fix in code:
   File: vonage_voice_bridge.py
   Function: vonage_event_callback()
   Line ~140: Should have "if status.lower() == 'answered':"
   
   If missing:
   > Replace the entire vonage_event_callback function with fixed version

3. Restart Django server:
   > python manage.py runserver 0.0.0.0:8002
   OR
   > daphne -b 0.0.0.0 -p 8002 project.asgi:application

4. Make another call to test


🚨 ISSUE #3: ngrok tunnel not working (can't connect)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symptom: Vonage can't reach webhook URL

Steps:
1. Check ngrok is running:
   > ngrok http 8002 --domain=uncontortioned-na-ponderously.ngrok-free.dev
   
   Should show:
   ✅ Session Status: active
   ✅ Forwarding to http://127.0.0.1:8002

2. Test webhook:
   > curl https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/ping/
   
   Should return: 200 OK

3. Restart ngrok if needed:
   > Ctrl+C to stop current ngrok
   > ngrok http 8002 --domain=uncontortioned-na-ponderously.ngrok-free.dev


🚨 ISSUE #4: Audio one-way (you hear agent but agent doesn't hear you)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symptom: Agent speaks but won't respond to your voice

Likely cause: Vonage → HumeAI audio stream broken

Steps:
1. Check Django logs for:
   ✅ Should see: "Received audio from Vonage"
   ✅ Should see: "Streaming to HumeAI"
   ✅ Should see: "Received response from HumeAI"
   
   ❌ If seeing errors: Check audio conversion

2. Verify audio format:
   Vonage sends: 16kHz linear16 PCM
   HumeAI expects: 48kHz linear16 PCM
   
   Should be converted automatically in:
   File: vonage_realtime_consumer.py
   Function: receive()

3. If audio conversion failing:
   Check: resampler module installed
   > pip install scipy librosa


🚨 ISSUE #5: HumeAI returns 401 (authentication error)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symptom: Logs show "401 Unauthorized from HumeAI"

Likely cause: Wrong endpoint or wrong auth header

Steps:
1. Verify endpoint in vonage_realtime_consumer.py:
   Line ~220: should be
   url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
   
   NOT:
   url = "wss://api.hume.ai/v0/evi/chat" (❌ Old, broken)

2. Verify auth header:
   Should have:
   headers = {"X-Hume-Api-Key": HUME_API_KEY}
   
   NOT:
   headers = {"Authorization": f"Bearer {HUME_API_KEY}"} (❌ Wrong)

3. Test directly:
   > python debug_hume_voice.py
   
   If test passes: Issue is elsewhere
   If test fails: Update credentials


✅ QUICK FIX CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before trying anything else, verify:

□ Django server running on 0.0.0.0:8002
  > python manage.py runserver 0.0.0.0:8002

□ ngrok tunnel active
  > ngrok http 8002 --domain=uncontortioned-na-ponderously.ngrok-free.dev

□ .env file has all credentials
  > VONAGE_API_KEY=bab7bfbe
  > VONAGE_APPLICATION_ID=0d75cbea-4319-434d-a864-f6f9ef83874d
  > HUME_API_KEY=mb5K22hbr...
  > HUME_CONFIG_ID=13624648-...

□ Database connected
  > python manage.py shell
  > from HumeAiTwilio.models import TwilioCall
  > TwilioCall.objects.count()  # Should return number > 0

□ HumeAI diagnostic passes
  > python debug_hume_voice.py
  > Should see 3 tests all PASS

□ vonage_voice_bridge.py has fix
  > Check function vonage_event_callback handles "answered"
  > Should return NCCO with stream action


🚨 NUCLEAR OPTION (Reset everything):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If nothing works, start fresh:

1. Stop everything:
   > Ctrl+C (Django)
   > Ctrl+C (ngrok)

2. Verify all components:
   > python final_checklist.py
   
   Should see all 7 checks PASS

3. If any check fails:
   > Re-run specific diagnostic:
   > python check_vonage_setup.py
   > python debug_hume_voice.py
   > python verify_hume_setup.py

4. Start fresh:
   > Restart Django
   > Restart ngrok
   > Make new call

5. Monitor logs closely:
   > tail -f logs/django.log
   > Look for every expected step


📊 KEY LOG INDICATORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Success indicators (should see all):
✅ "ANSWERED event detected"
✅ "Vonage WebSocket connection established"
✅ "Connected to HumeAI EVI"
✅ "Received audio from Vonage"
✅ "Streaming to HumeAI"
✅ "Received response from HumeAI"

Error indicators (investigation needed):
❌ "HumeAI connection failed" → Check endpoint/auth
❌ "WebSocket closed" → Check ngrok tunnel
❌ "NCCO stream setup failed" → Check vonage_voice_bridge.py fix
❌ "Audio conversion error" → Check resampler installed


🎯 FINAL CHECKLIST BEFORE CALLING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this before making any test call:

> python final_checklist.py

Expected output:
[✓] Vonage Configuration Ready
[✓] HumeAI Configuration Ready
[✓] Django Server Running
[✓] ngrok Tunnel Active
[✓] Database Connected
[✓] WebSocket Routes Configured
[✓] Fix Applied and Ready

Result: Ready to call!

If any check fails, don't proceed - fix that issue first!
"""

print(troubleshooting_steps)

# Create a function to run specific diagnostics
def run_diagnostic(diagnostic_type):
    import subprocess
    
    diagnostics = {
        'vonage': 'python check_vonage_setup.py',
        'hume': 'python debug_hume_voice.py',
        'django': 'python manage.py shell',
        'ngrok': 'curl https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/ping/',
        'full': 'python final_checklist.py'
    }
    
    if diagnostic_type in diagnostics:
        print(f"\n🔧 Running: {diagnostics[diagnostic_type]}")
        subprocess.run(diagnostics[diagnostic_type], shell=True)
    else:
        print("Available diagnostics: vonage, hume, django, ngrok, full")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_diagnostic(sys.argv[1])
    else:
        print("\nUsage: python troubleshoot.py [vonage|hume|django|ngrok|full]")
