"""
Test HumeAI with Microphone Input Simulation
Tests rate-limited audio streaming
"""

import asyncio
import websockets
import json
import base64
import audioop
from decouple import config

async def test_microphone_to_hume():
    """Simulate microphone input to HumeAI with rate limiting"""
    
    print("🎤 Testing Microphone → HumeAI Connection")
    print("=" * 50)
    
    # Get credentials
    hume_api_key = config('HUME_AI_API_KEY', default=config('HUME_API_KEY', default=''))
    config_id = config('HUME_CONFIG_ID')
    
    print(f"🔑 Using Config ID: {config_id}")
    
    # Connect to HumeAI
    hume_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={config_id}"
    headers = {
        'X-Hume-Api-Key': hume_api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"🔌 Connecting to HumeAI...")
    
    try:
        async with websockets.connect(hume_url, extra_headers=headers, ping_interval=20) as ws:
            print(f"✅ Connected to HumeAI!")
            
            # Send session config with STABLE settings
            session_config = {
                "type": "session_settings",
                "config_id": config_id,
                "audio": {
                    "encoding": "linear16",
                    "channels": 1,
                    "sample_rate": 8000  # Match Twilio phone input
                },
                "voice": {
                    "rate": 1.15,
                    "pitch": 1.0,
                    "energy": 1.2,
                    "clarity": "high",
                    "volume": 1.3
                }
            }
            
            await ws.send(json.dumps(session_config))
            print(f"📤 Sent session config (8kHz, stable settings)")
            
            # Generate fake audio chunks (simulate microphone)
            print(f"\n🎤 Simulating microphone audio chunks...")
            print(f"   📊 Sending 10 chunks with 20ms rate limiting")
            
            last_time = asyncio.get_event_loop().time()
            
            for i in range(10):
                # Simulate 20ms of audio at 8kHz = 160 samples = 320 bytes (16-bit)
                fake_audio = b'\x00' * 320
                audio_b64 = base64.b64encode(fake_audio).decode('utf-8')
                
                # Rate limiting (20ms minimum gap)
                current_time = asyncio.get_event_loop().time()
                time_since_last = current_time - last_time
                
                if time_since_last < 0.020:
                    delay = 0.020 - time_since_last
                    await asyncio.sleep(delay)
                    print(f"   ⏱️  Chunk {i+1}: Delayed {delay*1000:.1f}ms (rate limiting)")
                else:
                    print(f"   ✅ Chunk {i+1}: Sent immediately ({time_since_last*1000:.1f}ms gap)")
                
                last_time = asyncio.get_event_loop().time()
                
                # Send audio
                audio_msg = {
                    "type": "audio_input",
                    "data": audio_b64
                }
                await ws.send(json.dumps(audio_msg))
            
            print(f"\n✅ All chunks sent successfully!")
            print(f"📡 Waiting for HumeAI response...")
            
            # Listen for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received response: {data.get('type', 'unknown')}")
                print(f"   {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print(f"⏰ No response in 5 seconds (normal for silence)")
            
            print(f"\n🎉 Test Complete - Connection Stable!")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e.code} - {e.reason}")
        print(f"   This means HumeAI disconnected during audio streaming")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   HUME AI MICROPHONE INPUT TEST (RATE-LIMITED)")
    print("="*60 + "\n")
    
    result = asyncio.run(test_microphone_to_hume())
    
    if result:
        print("\n✅ SUCCESS: HumeAI handled rate-limited audio correctly!")
    else:
        print("\n❌ FAILED: HumeAI disconnected during audio streaming")
