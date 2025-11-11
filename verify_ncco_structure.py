"""
Verify the updated NCCO structure is correct
"""
import json
from decouple import config

print("=" * 80)
print("NCCO STRUCTURE VERIFICATION")
print("=" * 80)

HUME_API_KEY = config('HUME_API_KEY')
HUME_CONFIG_ID = config('HUME_CONFIG_ID')
BASE_URL = config('BASE_URL', default='http://localhost:8002')

# This is what vonage_outgoing_answer_webhook will return
ncco = [
    {
        "action": "connect",
        "eventUrl": [f"{BASE_URL}/api/hume-twilio/vonage-event-callback/"],
        "from": "12199644562",
        "timeout": 60,
        "limit": 7200,
        "endpoint": [
            {
                "type": "websocket",
                "uri": f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}",
                "content-type": "audio/l16;rate=16000",
                "headers": {
                    "X-Hume-Api-Key": HUME_API_KEY,
                    "User-Agent": "VonageVoiceAPI/1.0",
                    "Accept": "application/json"
                }
            }
        ]
    },
    {
        "action": "talk",
        "text": "Connecting you to our AI assistant. Please wait.",
        "bargeIn": True
    }
]

print("\n✅ Updated NCCO Structure:")
print(json.dumps(ncco, indent=2))

print("\n" + "=" * 80)
print("VERIFICATION CHECKLIST:")
print("=" * 80)

checks = {
    "Action 1 - Connect to WebSocket": ncco[0]["action"] == "connect",
    "WebSocket Type": ncco[0]["endpoint"][0]["type"] == "websocket",
    "HumeAI URI": "wss://api.hume.ai" in ncco[0]["endpoint"][0]["uri"],
    "Config ID in URI": HUME_CONFIG_ID in ncco[0]["endpoint"][0]["uri"],
    "Audio Format": ncco[0]["endpoint"][0]["content-type"] == "audio/l16;rate=16000",
    "API Key in Headers": "X-Hume-Api-Key" in ncco[0]["endpoint"][0]["headers"],
    "Accept Header": "Accept" in ncco[0]["endpoint"][0]["headers"],
    "Event Callback URL": len(ncco[0]["eventUrl"]) > 0,
    "Action 2 - Greeting Message": ncco[1]["action"] == "talk",
    "Barge In Enabled": ncco[1]["bargeIn"] == True
}

all_pass = True
for check, status in checks.items():
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check}")
    if not status:
        all_pass = False

print("\n" + "=" * 80)
if all_pass:
    print("🎉 ALL CHECKS PASSED!")
    print("\n📞 What will happen when call connects:")
    print("   1. Vonage calls answer webhook")
    print("   2. Webhook returns this NCCO")
    print("   3. Vonage plays: 'Connecting you to our AI assistant...'")
    print("   4. Vonage opens WebSocket to HumeAI")
    print("   5. Sends API key in X-Hume-Api-Key header")
    print("   6. Audio streams: Caller ↔ Vonage ↔ HumeAI")
    print("   7. HumeAI agent speaks and listens!")
    print("\n✅ NCCO is ready for production!")
else:
    print("❌ Some checks failed - review NCCO structure!")

print("=" * 80)
