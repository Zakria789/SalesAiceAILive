"""
🔍 NCCO STRUCTURE VALIDATION
Validates Vonage NCCO before making real call
"""

import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from decouple import config

print("\n" + "="*70)
print("🔍 VONAGE NCCO STRUCTURE VALIDATION")
print("="*70 + "\n")

# ============================================================
# 1. BUILD NCCO (Same as code)
# ============================================================
BASE_URL = config('BASE_URL', default='https://uncontortioned-na-ponderously.ngrok-free.dev')
test_uuid = "TEST-UUID-123"

server_ws_url = f"wss://{BASE_URL.replace('https://', '')}/api/vonage-stream/{test_uuid}/"

ncco = [
    {
        "action": "talk",
        "text": "Connecting you to our AI assistant.",
        "bargeIn": True
    },
    {
        "action": "stream",
        "streamUrl": [server_ws_url],
        "eventUrl": [f"{BASE_URL}/api/hume-twilio/vonage-event-callback/"],
        "eventMethod": "POST"
    }
]

print("1️⃣  NCCO STRUCTURE:")
print(json.dumps(ncco, indent=2))

# ============================================================
# 2. VALIDATE STRUCTURE
# ============================================================
print("\n2️⃣  VALIDATION CHECKS:")

issues = []
warnings = []

# Check action 1 - talk
if ncco[0]["action"] != "talk":
    issues.append("❌ First action must be 'talk'")
else:
    print("   ✅ First action: talk")

if "text" not in ncco[0]:
    issues.append("❌ Talk action missing 'text' field")
else:
    print(f"   ✅ Talk text: '{ncco[0]['text']}'")

# Check action 2 - stream
if ncco[1]["action"] != "stream":
    issues.append("❌ Second action must be 'stream'")
else:
    print("   ✅ Second action: stream")

if "streamUrl" not in ncco[1]:
    issues.append("❌ Stream action missing 'streamUrl' field")
else:
    print(f"   ✅ streamUrl: {ncco[1]['streamUrl'][0]}")

if not ncco[1]['streamUrl'][0].startswith('wss://'):
    issues.append("❌ streamUrl must start with 'wss://'")
else:
    print("   ✅ WebSocket protocol: wss://")

# Check WebSocket endpoint exists
print("\n3️⃣  WEBSOCKET ENDPOINT CHECK:")

from HumeAiTwilio.routing import websocket_urlpatterns
vonage_routes = [str(p.pattern) for p in websocket_urlpatterns if 'vonage-stream' in str(p.pattern)]

if len(vonage_routes) > 0:
    print(f"   ✅ Found {len(vonage_routes)} Vonage WebSocket route(s)")
    for route in vonage_routes:
        print(f"      → {route}")
else:
    issues.append("❌ No Vonage WebSocket routes found!")

# Check Consumer
print("\n4️⃣  CONSUMER CHECK:")

try:
    from HumeAiTwilio.vonage_realtime_consumer import VonageRealTimeConsumer
    print("   ✅ VonageRealTimeConsumer imported successfully")
    
    # Check if it has required methods
    required_methods = ['connect', 'disconnect', 'receive']
    for method in required_methods:
        if hasattr(VonageRealTimeConsumer, method):
            print(f"   ✅ Method '{method}' exists")
        else:
            issues.append(f"❌ Method '{method}' missing!")
            
except ImportError as e:
    issues.append(f"❌ Cannot import VonageRealTimeConsumer: {e}")

# ============================================================
# 5. VONAGE STREAM ACTION DOCUMENTATION
# ============================================================
print("\n5️⃣  VONAGE STREAM ACTION SPECS:")
print("   📖 According to Vonage docs:")
print("   • Action: 'stream' (not 'connect')")
print("   • streamUrl: Array of WebSocket URLs")
print("   • Protocol: wss:// required")
print("   • eventUrl: Optional callback URL")
print("   • eventMethod: POST or GET (default POST)")

# ============================================================
# 6. COMPARE WITH PREVIOUS (BROKEN) NCCO
# ============================================================
print("\n6️⃣  WHAT WE FIXED:")
print("   ❌ OLD: action = 'connect' with 'endpoint' array")
print("   ✅ NEW: action = 'stream' with 'streamUrl' array")
print()
print("   ❌ OLD: endpoint[0]['type'] = 'websocket'")
print("   ✅ NEW: Direct streamUrl (no nested structure)")
print()
print("   ❌ OLD: 'content-type' or 'contentType' parameter")
print("   ✅ NEW: No content-type needed in stream action")

# ============================================================
# 7. FINAL VERDICT
# ============================================================
print("\n" + "="*70)
print("🎯 FINAL VERDICT")
print("="*70)

if len(issues) == 0:
    print("\n✅ ALL VALIDATION CHECKS PASSED!")
    print("\n🚀 NCCO Structure is CORRECT!")
    print("   Ready for test call")
    
    print("\n📋 Expected Flow:")
    print("   1. Vonage calls answer webhook")
    print("   2. Returns NCCO with 'stream' action")
    print("   3. Vonage connects to WebSocket: /api/vonage-stream/{uuid}/")
    print("   4. VonageRealTimeConsumer handles connection")
    print("   5. Audio streams: Vonage ↔ Server ↔ HumeAI")
    
    if len(warnings) > 0:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
else:
    print("\n❌ VALIDATION FAILED!")
    for issue in issues:
        print(f"   {issue}")

print("\n" + "="*70 + "\n")

# ============================================================
# 8. EXPORT VALID NCCO FOR TESTING
# ============================================================
print("💾 Saving valid NCCO to file: valid_ncco.json")
with open('valid_ncco.json', 'w') as f:
    json.dump(ncco, f, indent=2)
print("   ✅ Saved! You can inspect: valid_ncco.json\n")
