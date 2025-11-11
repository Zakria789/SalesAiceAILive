"""
Test if WebSocket URL is accessible
"""
import asyncio
import websockets

# Test URL
ws_url = "wss://uncontortioned-na-ponderously.ngrok-free.dev/api/vonage-stream/TEST-UUID/"

async def test_websocket():
    print(f"\n🔍 Testing WebSocket URL:")
    print(f"   {ws_url}\n")
    
    try:
        print("📡 Attempting connection...")
        async with websockets.connect(ws_url, timeout=5) as ws:
            print("✅ WebSocket connection successful!")
            print(f"   Protocol: {ws.protocol}")
            print(f"   State: {ws.state}")
            await ws.close()
            print("✅ Connection closed cleanly\n")
            return True
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e.status_code}")
        print(f"   Headers: {e.headers}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}")
        print(f"   Error: {str(e)}\n")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    
    if result:
        print("🎯 WebSocket URL is VALID and ACCESSIBLE!")
    else:
        print("⚠️  WebSocket URL has issues - Vonage cannot connect!")
        print("\n💡 Possible issues:")
        print("   1. Ngrok tunnel not running")
        print("   2. Django server not running")
        print("   3. WebSocket route not registered")
        print("   4. Ngrok requires authentication")
