#!/usr/bin/env python
"""
Test Vonage + HumeAI Emotion Capture Complete Flow
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.vonage_voice_bridge import initiate_vonage_call
from HumeAiTwilio.models import ConversationLog, TwilioCall
import time

def main():
    print("=" * 70)
    print("VONAGE + HUMEAI EMOTION CAPTURE TEST")
    print("=" * 70)
    
    # Test phone number
    to_number = "+923403471112"
    
    print(f"\n1. Initiating Vonage call to {to_number}...")
    
    # Make the call
    result = initiate_vonage_call(to_number)
    
    if not result.get('success'):
        print(f"❌ Call failed: {result.get('error')}")
        return
    
    call_uuid = result.get('call_uuid')
    print(f"✅ Call initiated!")
    print(f"   UUID: {call_uuid}")
    print(f"   Call ID: {result.get('call_id')}")
    print(f"   From: {result.get('from')}")
    print(f"   To: {result.get('to')}")
    print(f"   Status: {result.get('status')}")
    
    print("\n2. Waiting for recording to complete...")
    print("   (Vonage will record the call and send webhook)")
    print("   (Recording → HumeAI → Emotions → Database)")
    
    # Wait for recording callback (this happens asynchronously via webhook)
    print("\n3. Checking for emotion data...")
    
    for attempt in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        
        try:
            # Check if emotion data was saved
            logs = ConversationLog.objects.filter(
                call__call_sid=call_uuid
            ).order_by('-timestamp')
            
            if logs.exists():
                print(f"\n✅ Emotion data found!")
                
                for i, log in enumerate(logs, 1):
                    print(f"\n   Log {i}:")
                    print(f"   - Message: {log.message}")
                    print(f"   - Emotion Scores: {log.emotion_scores}")
                    print(f"   - Sentiment: {log.sentiment}")
                    print(f"   - Confidence: {log.confidence}")
                
                print("\n" + "=" * 70)
                print("✅ TEST COMPLETE - EMOTIONS CAPTURED!")
                print("=" * 70)
                return
        
        except Exception as e:
            pass
        
        print(f"   Waiting... (attempt {attempt+1}/30)")
    
    print("\n⚠️  No emotion data found after 30 seconds")
    print("   (Webhook may not have been triggered)")
    print("   Check Django console for error logs")


if __name__ == '__main__':
    main()
