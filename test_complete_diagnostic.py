"""
🔍 COMPLETE WEBHOOK + WEBSOCKET DIAGNOSTIC
Check server, ngrok, and all connections
"""

import os
import sys
import requests
import socket
from decouple import config

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_local_server():
    """Test local Django server"""
    print("\n" + "="*70)
    print("🔍 CHECKING LOCAL DJANGO SERVER")
    print("="*70)
    
    port = 8002
    
    if check_port('127.0.0.1', port):
        print(f"✅ Server running on port {port}")
        
        # Test endpoint
        try:
            response = requests.post(
                f'http://127.0.0.1:{port}/api/hume-twilio/voice-webhook/',
                data={'test': 'data'},
                timeout=5
            )
            print(f"✅ Webhook endpoint responding: {response.status_code}")
            return True
        except Exception as e:
            print(f"⚠️  Endpoint error: {e}")
            return False
    else:
        print(f"❌ No server running on port {port}")
        print(f"\n💡 Start server with:")
        print(f"   python manage.py runserver 8002")
        return False

def test_ngrok():
    """Test ngrok connection"""
    print("\n" + "="*70)
    print("🔍 CHECKING NGROK TUNNEL")
    print("="*70)
    
    ngrok_url = config('BASE_URL', default='')
    
    if not ngrok_url:
        print("❌ No BASE_URL found in .env")
        return False
    
    print(f"📍 Configured URL: {ngrok_url}")
    
    # Check ngrok API
    if check_port('127.0.0.1', 4040):
        print("✅ Ngrok API accessible on port 4040")
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
            tunnels = response.json().get('tunnels', [])
            
            if tunnels:
                print(f"✅ Found {len(tunnels)} active tunnel(s):")
                for tunnel in tunnels:
                    print(f"   - {tunnel['public_url']} → {tunnel['config']['addr']}")
                return True
            else:
                print("⚠️  Ngrok API running but no tunnels found")
                return False
        except Exception as e:
            print(f"⚠️  Ngrok API error: {e}")
            return False
    else:
        print("❌ Ngrok not running (port 4040 closed)")
        print("\n💡 Start ngrok with:")
        print("   ngrok http 8002")
        print("\n💡 Or use ngrok authtoken:")
        print("   ngrok config add-authtoken YOUR_TOKEN")
        return False

def test_websocket_route():
    """Test WebSocket routing configuration"""
    print("\n" + "="*70)
    print("🔍 CHECKING WEBSOCKET CONFIGURATION")
    print("="*70)
    
    try:
        # Check ASGI configuration
        from core.asgi import application
        print("✅ ASGI application loaded")
        
        # Check routing
        from HumeAiTwilio.routing import websocket_urlpatterns
        print(f"✅ WebSocket patterns registered: {len(websocket_urlpatterns)}")
        
        for pattern in websocket_urlpatterns:
            print(f"   - {pattern.pattern}")
        
        return True
    except Exception as e:
        print(f"❌ WebSocket config error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_twilio_config():
    """Test Twilio configuration"""
    print("\n" + "="*70)
    print("🔍 CHECKING TWILIO CONFIGURATION")
    print("="*70)
    
    try:
        from twilio.rest import Client
        
        sid = config('TWILIO_ACCOUNT_SID', default='')
        token = config('TWILIO_AUTH_TOKEN', default='')
        phone = config('TWILIO_PHONE_NUMBER', default='')
        
        if not all([sid, token, phone]):
            print("❌ Missing Twilio credentials in .env")
            return False
        
        print(f"✅ Account SID: {sid[:10]}...")
        print(f"✅ Phone: {phone}")
        
        client = Client(sid, token)
        account = client.api.accounts(sid).fetch()
        print(f"✅ Account Status: {account.status}")
        
        return True
    except Exception as e:
        print(f"❌ Twilio error: {e}")
        return False

def main():
    print("\n" + "🚀"*35)
    print("COMPLETE WEBHOOK + WEBSOCKET DIAGNOSTIC")
    print("🚀"*35)
    
    results = {
        'Django Server': test_local_server(),
        'Ngrok Tunnel': test_ngrok(),
        'WebSocket Config': test_websocket_route(),
        'Twilio Config': test_twilio_config(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*70)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'OK' if status else 'ISSUE'}")
    
    print("\n" + "="*70)
    
    if all(results.values()):
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n✅ Ready for:")
        print("   1. WebSocket connections")
        print("   2. Twilio voice calls")
        print("   3. HumeAI integration")
        
        print("\n📞 Test with:")
        print("   python test_live_call.py --phone +1234567890")
    else:
        print("⚠️  ISSUES FOUND - Fix the problems above")
        
        if not results['Django Server']:
            print("\n🔧 Start Django:")
            print("   python manage.py runserver 8002")
        
        if not results['Ngrok Tunnel']:
            print("\n🔧 Start Ngrok:")
            print("   ngrok http 8002")
            print("   (or configure authtoken first)")
    
    print("\n")

if __name__ == "__main__":
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    import django
    django.setup()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
