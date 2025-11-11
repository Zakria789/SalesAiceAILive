"""
🎤 HumeAI Voice Speed Update Script
=====================================
Use this script to update voice speed via API if dashboard doesn't have the setting.
"""

import requests
import json
from decouple import config

# Your HumeAI credentials (from .env)
API_KEY = config('HUME_API_KEY')
CONFIG_ID = config('HUME_CONFIG_ID', default='13624648-658a-49b1-81cb-a0f2e2b05de5')

def get_current_config():
    """Fetch current configuration to see what settings exist"""
    url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"
    headers = {
        "X-Hume-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("🔍 Fetching current configuration...\n")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        config = response.json()
        print("✅ Current Configuration:")
        print("=" * 80)
        print(json.dumps(config, indent=2))
        print("=" * 80)
        
        # Check if voice settings exist
        if 'voice' in config:
            print("\n✅ Voice settings found:")
            print(f"   Provider: {config['voice'].get('provider', 'N/A')}")
            print(f"   Current Speed: {config['voice'].get('speed', 'N/A')}")
        else:
            print("\n⚠️ No voice settings found in current config")
        
        return config
    else:
        print(f"❌ Error fetching config: {response.status_code}")
        print(response.text)
        return None

def update_voice_speed(speed=1.4):
    """Update voice speed to specified value"""
    url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"
    headers = {
        "X-Hume-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Try different payload structures based on HumeAI API version
    payloads = [
        # Structure 1: Direct voice object
        {
            "voice": {
                "provider": "HUME_AI",
                "speed": speed
            }
        },
        # Structure 2: TTS settings
        {
            "tts_settings": {
                "speed": speed,
                "rate": speed
            }
        },
        # Structure 3: Prosody settings
        {
            "prosody": {
                "rate": speed,
                "speed": speed
            }
        }
    ]
    
    print(f"\n🎯 Attempting to update voice speed to {speed}x...")
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n📤 Attempt {i}: Trying payload structure {i}...")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS! Voice speed updated to {speed}x")
            print("=" * 80)
            print(json.dumps(response.json(), indent=2))
            print("=" * 80)
            print("\n🎉 Changes applied! Make a test call to hear the difference.")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
    
    print("\n❌ All payload structures failed. Voice speed may need to be set via dashboard.")
    return False

def main():
    print("=" * 80)
    print("🎤 HUMEAI VOICE SPEED UPDATE TOOL")
    print("=" * 80)
    print(f"Config ID: {CONFIG_ID}")
    print(f"Target Speed: 1.4x (40% faster than default)\n")
    
    # Step 1: Get current config
    current_config = get_current_config()
    
    if current_config:
        print("\n" + "=" * 80)
        user_input = input("\n📝 Do you want to update voice speed to 1.4x? (y/n): ").lower()
        
        if user_input == 'y':
            # Step 2: Update speed
            success = update_voice_speed(speed=1.4)
            
            if success:
                print("\n✅ DONE! Next steps:")
                print("   1. No need to restart Django server")
                print("   2. Run: python quick_call_test.py")
                print("   3. Answer call and listen to faster AI voice!")
            else:
                print("\n⚠️ API update failed. Please update via HumeAI Dashboard:")
                print("   1. Go to: https://platform.hume.ai/")
                print("   2. Edit config: 13624648-658a-49b1-81cb-a0f2e2b05de5")
                print("   3. Find 'Voice' or 'Speech' settings")
                print("   4. Adjust 'Speech Rate' slider to 1.4x")
                print("   5. Save configuration")
        else:
            print("\n⏸️ Update cancelled.")
    else:
        print("\n❌ Could not fetch current configuration. Check your API key and config ID.")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
