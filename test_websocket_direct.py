"""
Test WebSocket Connection Directly
"""
import asyncio
import websockets
import json

NGROK_URL = "https://uncontortioned-na-ponderously.ngrok-free.dev"
WS_URL = NGROK_URL.replace('https://', 'wss://') + "/ws/hume-twilio/stream/TEST123/"

async def test_websocket():
    print(f"\n🔌 Testing WebSocket Connection:")
    print(f"URL: {WS_URL}\n")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket connected!")
            
            # Send test message
            test_msg = {
                "event": "connected",
                "streamSid": "TEST123"
            }
            await websocket.send(json.dumps(test_msg))
            print(f"📤 Sent: {test_msg}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⚠️  No response received (timeout)")
            
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
