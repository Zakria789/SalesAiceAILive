"""
Test different HumeAI session configurations
To find which one works stable
"""
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_config(config_name, session_config):
    """Test a specific session configuration"""
    
    api_key = os.getenv("HUME_API_KEY")
    config_id = os.getenv("HUME_CONFIG_ID")
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {config_name}")
    print(f"{'='*60}")
    
    try:
        url = f"wss://api.hume.ai/v0/assistant/chat?config_id={config_id}"
        headers = {
            'X-Hume-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"🔌 Connecting...")
        ws = await asyncio.wait_for(
            websockets.connect(url, extra_headers=headers, ping_interval=20, ping_timeout=20),
            timeout=10.0
        )
        print(f"✅ Connected!")
        
        if session_config:
            print(f"📤 Sending config: {json.dumps(session_config, indent=2)}")
            await ws.send(json.dumps(session_config))
            print(f"✅ Config sent!")
        else:
            print(f"⏭️  Skipping session config")
        
        # Wait and listen for 10 seconds
        print(f"👂 Listening for 10 seconds...")
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < 10:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(message)
                msg_type = data.get('type', 'unknown')
                print(f"   📨 Received: {msg_type}")
                
                if msg_type == 'error':
                    print(f"   ❌ Error: {data}")
                    
            except asyncio.TimeoutError:
                # No message, that's OK
                pass
        
        # Check connection status
        if not ws.closed:
            print(f"✅ Connection STABLE after 10 seconds!")
            print(f"🎉 {config_name} - PASSED!")
            await ws.close()
            return True
        else:
            print(f"❌ Connection CLOSED!")
            print(f"   Close code: {ws.close_code}")
            print(f"   Close reason: {ws.close_reason}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        return False

async def run_tests():
    """Run all configuration tests"""
    
    print("\n" + "="*60)
    print("🧪 HUME AI SESSION CONFIG TESTS")
    print("="*60)
    
    results = {}
    
    # Test 1: No session config
    results["No Config"] = await test_config(
        "No Session Config",
        None
    )
    
    await asyncio.sleep(2)
    
    # Test 2: Minimal config (only audio)
    results["Minimal"] = await test_config(
        "Minimal Config (audio only)",
        {
            "type": "session_settings",
            "audio": {
                "encoding": "linear16",
                "channels": 1,
                "sample_rate": 48000
            }
        }
    )
    
    await asyncio.sleep(2)
    
    # Test 3: With config_id in session
    results["With Config ID"] = await test_config(
        "Config with config_id",
        {
            "type": "session_settings",
            "config_id": os.getenv("HUME_CONFIG_ID"),
            "audio": {
                "encoding": "linear16",
                "channels": 1,
                "sample_rate": 48000
            }
        }
    )
    
    await asyncio.sleep(2)
    
    # Test 4: Original extreme settings
    results["Extreme Voice"] = await test_config(
        "Extreme Voice Settings",
        {
            "type": "session_settings",
            "config_id": os.getenv("HUME_CONFIG_ID"),
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
    )
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20s} : {status}")
    
    print("\n" + "="*60)
    
    # Recommendation
    passing = [name for name, passed in results.items() if passed]
    if passing:
        print(f"✅ RECOMMENDATION: Use '{passing[0]}' configuration")
    else:
        print(f"❌ All tests failed - check API credentials")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
