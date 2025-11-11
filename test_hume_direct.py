"""
Test HumeAI API directly - check if config is valid and accessible
"""
import asyncio
import websockets
import json
from decouple import config

async def test_hume_websocket():
    """Test HumeAI WebSocket connection directly"""
    
    config_id = config('HUME_CONFIG_ID')
    api_key = config('HUME_API_KEY')
    secret_key = config('HUME_SECRET_KEY')
    
    # HumeAI WebSocket URL
    ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={config_id}"
    
    print("=" * 80)
    print("HUMEAI WEBSOCKET CONNECTION TEST")
    print("=" * 80)
    print(f"\n🔗 Connecting to: {ws_url}")
    print(f"📋 Config ID: {config_id}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    try:
        # Headers for authentication
        headers = {
            "X-Hume-Api-Key": api_key,
            "X-Hume-Secret-Key": secret_key,
        }
        
        print(f"\n⏳ Attempting connection...")
        
        # Connect to WebSocket
        async with websockets.connect(
            ws_url,
            extra_headers=headers,
            ping_interval=30,
            ping_timeout=10
        ) as websocket:
            
            print(f"✅ Connected successfully!")
            
            # Wait for initial message
            print(f"\n⏳ Waiting for server response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)
            
            print(f"\n📨 Received message:")
            print(f"   Type: {data.get('type')}")
            
            if data.get('type') == 'chat_metadata':
                print(f"   ✅ Chat metadata received!")
                print(f"   Chat ID: {data.get('chat_id')}")
                print(f"   Chat Group ID: {data.get('chat_group_id')}")
            
            # Try sending a test message
            print(f"\n📤 Sending test message...")
            test_msg = {
                "type": "user_message",
                "message": {
                    "role": "user",
                    "content": "Hello, can you hear me?"
                }
            }
            await websocket.send(json.dumps(test_msg))
            print(f"   ✅ Message sent!")
            
            # Wait for response
            print(f"\n⏳ Waiting for AI response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=15)
            data = json.loads(response)
            
            print(f"\n📨 AI Response:")
            print(f"   Type: {data.get('type')}")
            if data.get('type') == 'agent_message':
                print(f"   ✅ Agent responded!")
                msg = data.get('message', {})
                print(f"   Role: {msg.get('role')}")
                print(f"   Content: {msg.get('content', '')[:100]}...")
            
            print(f"\n" + "=" * 80)
            print("✅ HUMEAI API TEST: SUCCESS!")
            print("=" * 80)
            print("   ✅ WebSocket connection: Working")
            print("   ✅ Authentication: Valid")
            print("   ✅ Config ID: Active")
            print("   ✅ Agent response: Received")
            print("\n💡 HumeAI API is working perfectly!")
            print("   Problem is likely Vonage → HumeAI connection via ngrok")
            print("=" * 80)
            
    except asyncio.TimeoutError:
        print(f"\n❌ TIMEOUT: No response from HumeAI server")
        print(f"   Config might be inactive or deleted")
        
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n❌ CONNECTION FAILED: {e}")
        print(f"   Status code: {e.status_code}")
        if e.status_code == 401:
            print(f"   ❌ Authentication failed - Invalid API key or secret")
        elif e.status_code == 404:
            print(f"   ❌ Config not found - Invalid config_id")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hume_websocket())
