#!/usr/bin/env python
"""
🚀 FINAL LIVE CALL EXECUTION GUIDE
Step-by-step commands to run
"""

print("""
================================================================================
🎬 LIVE CALL EXECUTION - FINAL STEPS
Customer + HumeAI Agent Real-Time Conversation
================================================================================

📋 IMPORTANT REMINDERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  DONON SERVERS BNANA ZAROORI HAY:
    1. Django Daphne Server (Terminal 1) - MUST BE RUNNING
    2. Call Initiation Script (Terminal 2) - Make the call

❌ STEP 1 SKIP KARO TO CALL FAIL HOGA!
❌ STEP 2 SKIP KARO TO CALL INITIATE NHI HOGA!

BOTH REQUIRED! 🔴


✅ STEP 1: Start Django Daphne Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Open NEW Terminal (Terminal 1)

Run these commands ONE BY ONE:

1. Navigate to project:
   $ cd e:\\Python-AI\\Django-Backend\\TESTREPO

2. Activate virtual environment:
   $ .\\venv\\Scripts\\Activate

3. Start Django Daphne ASGI server:
   $ daphne -b 0.0.0.0 -p 8002 core.asgi:application

WAIT FOR this output:
   ✅ Loaded calls WebSocket routing
   ✅ Loaded HumeAiTwilio WebSocket routing
   ✅ 6 WebSocket route(s) registered
   ✅ Daphne server starting
   ✅ HTTP/2 support enabled
   ✅ Listening on http://0.0.0.0:8002

🔴 KEEP THIS TERMINAL OPEN! Do NOT close it!
   This server handles all WebSocket connections and HumeAI bridging.


✅ STEP 2: Make the Call
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Open ANOTHER Terminal (Terminal 2)

Run these commands ONE BY ONE:

1. Navigate to project:
   $ cd e:\\Python-AI\\Django-Backend\\TESTREPO

2. Activate virtual environment:
   $ .\\venv\\Scripts\\Activate

3. Make the call:
   $ python vonage_sdk_call.py

EXPECT this output:
   ✅ Configuration loaded
   ✅ Private key loaded
   ✅ Vonage client created with JWT auth
   ✅ Making call...
   ✅ Response: HTTP 201 CREATED
   ✅ UUID: [call-id-here]
   ✅ Status: RINGING


📞 AT THIS POINT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phone number +923403471112 is RINGING!

You have 3 options:
1. Answer the call (Pick up phone)
2. Let it ring (Test connection)
3. Cancel (Ctrl+C in Terminal 2)

🎯 If you ANSWER:
   - You will be connected to HumeAI agent
   - Agent will greet you
   - You can talk to it
   - Agent will respond with voice 🎙️
   - Real-time emotions will be tracked
   - Everything recorded in database


🔍 WHAT TO WATCH IN TERMINAL 1 (Django Server):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When you answer the phone, Terminal 1 will show:

[1] WebSocket Connection:
    🔗 Vonage WebSocket connection established
    📞 Vonage stream started: UUID=...

[2] HumeAI Connection:
    ✅ Connected to HumeAI EVI for Vonage call
    📤 Sent session config to HumeAI

[3] Audio Streaming:
    🎵 Received audio chunk (from phone)
    🔄 Converting audio: 16kHz → 48kHz
    📤 Sending to HumeAI

[4] HumeAI Response:
    💬 Assistant Response: [message text]
    🎵 Audio Output: 128060 bytes
    🔄 Converting audio: 48kHz → 16kHz
    📤 Sending to phone

[5] Emotions:
    😊 Emotions detected: joy=0.8, engagement=0.9

[6] Repeat:
    - Customer speaks
    - HumeAI responds
    - Emotions logged
    - Continue conversation


💾 DATABASE RECORDING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After call ends, check database:

$ python manage.py shell

>>> from HumeAiTwilio.models import TwilioCall
>>> call = TwilioCall.objects.order_by('-created_at').first()
>>> print(f"Duration: {call.duration} seconds")
>>> print(f"Emotions logged: {call.hume_emotions.count()}")
>>> print(f"Conversation: {call.conversation[:100]}...")


⏹️  TO STOP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminal 2 (Call script): 
   Press Ctrl+C or just wait for call to end

Terminal 1 (Django server):
   Press Ctrl+C to stop (but keep it running for future calls)

HANGUP call from phone to end conversation


🎉 SUCCESS CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Call initiated: HTTP 201 ✓
✅ Phone received: Ringing ✓
✅ WebSocket opened: ✓
✅ HumeAI connected: ✓
✅ Customer speaks: Recognized ✓
✅ HumeAI responds: Text + Audio ✓
✅ Customer hears: Voice response 🎙️ ✓
✅ Emotions logged: Database ✓
✅ Call recorded: TwilioCall table ✓


🚀 READY? Let's go!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminal 1: daphne -b 0.0.0.0 -p 8002 core.asgi:application
Terminal 2: python vonage_sdk_call.py
Phone: Answer when it rings
HumeAI: Talk to the agent!


================================================================================
""")
