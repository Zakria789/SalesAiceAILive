"""
Test HumeAI WebSocket Connection
Quick test to verify HumeAI connectivity before running full server
"""
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_hume_connection():
    """Test HumeAI WebSocket connection"""
    
    # Get credentials
    api_key = os.getenv("HUME_API_KEY")
    secret_key = os.getenv("HUME_SECRET_KEY")
    config_id = os.getenv("HUME_CONFIG_ID")
    
    print("=" * 60)
    print("🧪 TESTING HUME AI CONNECTION")
    print("=" * 60)
    
    # Check credentials
    if not api_key:
        print("❌ HUME_API_KEY not found in .env")
        return False
    if not secret_key:
        print("❌ HUME_SECRET_KEY not found in .env")
        return False
    if not config_id:
        print("❌ HUME_CONFIG_ID not found in .env")
        return False
    
    print(f"✅ API Key: {api_key[:20]}...")
    print(f"✅ Secret Key: {secret_key[:20]}...")
    print(f"✅ Config ID: {config_id}")
    print()
    
    # Test connection
    try:
        url = f"wss://api.hume.ai/v0/assistant/chat?config_id={config_id}"
        headers = {
            'X-Hume-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"🔌 Connecting to HumeAI...")
        print(f"🌐 URL: {url}")
        print()
        
        # Connect with timeout
        ws = await asyncio.wait_for(
            websockets.connect(url, extra_headers=headers, ping_interval=20, ping_timeout=20),
            timeout=10.0
        )
        
        print("✅ WebSocket connected successfully!")
        print()
        
        # Send session config (same as your code)
        session_config = {
            "type": "session_settings",
            "config_id": config_id,
            "audio": {
                "encoding": "linear16",
                "channels": 1,
                "sample_rate": 48000
            },
            "voice": {
                "rate": 3.2,
                "pitch": 1.2,
                "energy": 3.0,
                "clarity": "ultra",
                "volume": 2.5
            }
        }
        
        print("📤 Sending session config...")
        await ws.send(json.dumps(session_config))
        print("✅ Session config sent!")
        print()
        
        # Wait for response (5 seconds)
        print("👂 Listening for HumeAI response...")
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"📨 Received: {data.get('type', 'unknown')}")
            print(f"📄 Full message: {json.dumps(data, indent=2)}")
            print()
        except asyncio.TimeoutError:
            print("⏰ No response in 5 seconds (this is OK if connection stays open)")
            print()
        
        # Check if connection is still open
        if not ws.closed:
            print("✅ Connection is OPEN and STABLE!")
            print("🎉 HumeAI connection test PASSED!")
            await ws.close()
            return True
        else:
            print(f"❌ Connection CLOSED unexpectedly!")
            print(f"   Close code: {ws.close_code}")
            print(f"   Close reason: {ws.close_reason}")
            return False
            
    except asyncio.TimeoutError:
        print("❌ Connection timeout after 10 seconds")
        print("   Check: Internet connection, API credentials, HumeAI service")
        return False
        
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ HumeAI rejected connection: HTTP {e.status_code}")
        print(f"   Check: API credentials and config ID")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        return False
    
    finally:
        print()
        print("=" * 60)

if __name__ == "__main__":
    print()
    result = asyncio.run(test_hume_connection())
    print()
    
    if result:
        print("✅ ✅ ✅  ALL TESTS PASSED  ✅ ✅ ✅")
        print("Ready to start Django server!")
    else:
        print("❌ ❌ ❌  TESTS FAILED  ❌ ❌ ❌")
        print("Fix the issues before starting server")
    
    print()
