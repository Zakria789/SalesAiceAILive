"""
Deep NCCO Validation for Vonage
Tests NCCO structure against Vonage specification
"""
import json

def validate_ncco_structure():
    """Validate NCCO against Vonage requirements"""
    
    print("="*70)
    print("🔍 VONAGE NCCO DEEP VALIDATION")
    print("="*70)
    
    # Our current NCCO
    ncco = [
        {
            "action": "talk",
            "text": "Connecting you to our AI assistant."
        },
        {
            "action": "connect",
            "endpoint": [
                {
                    "type": "websocket",
                    "uri": "wss://uncontortioned-na-ponderously.ngrok-free.dev/api/vonage-stream/TEST-UUID/",
                    "content-type": "audio/l16;rate=16000"
                }
            ]
        }
    ]
    
    print("\n📋 Current NCCO Structure:")
    print(json.dumps(ncco, indent=2))
    
    # Validation checks
    print("\n🔍 VALIDATION CHECKS:")
    print("-" * 70)
    
    errors = []
    warnings = []
    
    # Check 1: Is valid JSON?
    try:
        json_str = json.dumps(ncco)
        json.loads(json_str)
        print("✅ Valid JSON format")
    except Exception as e:
        errors.append(f"Invalid JSON: {e}")
        print(f"❌ Invalid JSON: {e}")
    
    # Check 2: Is array?
    if isinstance(ncco, list):
        print("✅ NCCO is an array")
    else:
        errors.append("NCCO must be an array")
        print("❌ NCCO must be an array")
    
    # Check 3: Has actions?
    if len(ncco) > 0:
        print(f"✅ Contains {len(ncco)} action(s)")
    else:
        errors.append("NCCO must contain at least one action")
        print("❌ NCCO must contain at least one action")
    
    # Check 4: Validate each action
    for idx, action in enumerate(ncco):
        print(f"\n  🔹 Action {idx + 1}: {action.get('action', 'MISSING')}")
        
        # Must have 'action' field
        if 'action' not in action:
            errors.append(f"Action {idx + 1}: Missing 'action' field")
            print(f"    ❌ Missing 'action' field")
            continue
        
        action_type = action['action']
        print(f"    ✅ Action type: '{action_type}'")
        
        # Validate TALK action
        if action_type == 'talk':
            if 'text' in action:
                print(f"    ✅ Has 'text' field")
                if isinstance(action['text'], str):
                    print(f"    ✅ Text is string ({len(action['text'])} chars)")
                else:
                    errors.append(f"Action {idx + 1}: 'text' must be string")
                    print(f"    ❌ 'text' must be string")
            else:
                errors.append(f"Action {idx + 1}: 'talk' requires 'text' field")
                print(f"    ❌ 'talk' requires 'text' field")
            
            # Check for invalid fields
            valid_talk_fields = ['action', 'text', 'bargeIn', 'loop', 'level', 
                                'language', 'style', 'premium', 'voiceName']
            for field in action.keys():
                if field not in valid_talk_fields:
                    warnings.append(f"Action {idx + 1}: Unknown field '{field}' in talk action")
                    print(f"    ⚠️  Unknown field '{field}'")
        
        # Validate CONNECT action
        elif action_type == 'connect':
            if 'endpoint' in action:
                print(f"    ✅ Has 'endpoint' field")
                
                if isinstance(action['endpoint'], list):
                    print(f"    ✅ Endpoint is array ({len(action['endpoint'])} endpoint(s))")
                    
                    # Validate endpoint structure
                    for ep_idx, endpoint in enumerate(action['endpoint']):
                        print(f"      🔸 Endpoint {ep_idx + 1}:")
                        
                        if 'type' not in endpoint:
                            errors.append(f"Action {idx + 1}, Endpoint {ep_idx + 1}: Missing 'type' field")
                            print(f"        ❌ Missing 'type' field")
                        else:
                            ep_type = endpoint['type']
                            print(f"        ✅ Type: '{ep_type}'")
                            
                            if ep_type == 'websocket':
                                # Validate websocket endpoint
                                if 'uri' in endpoint:
                                    uri = endpoint['uri']
                                    print(f"        ✅ Has 'uri' field")
                                    
                                    if isinstance(uri, str):
                                        print(f"        ✅ URI is string")
                                        
                                        # Check URI format
                                        if uri.startswith('wss://') or uri.startswith('ws://'):
                                            print(f"        ✅ Valid WebSocket protocol")
                                        else:
                                            errors.append(f"Action {idx + 1}: WebSocket URI must start with ws:// or wss://")
                                            print(f"        ❌ Invalid WebSocket protocol")
                                        
                                        # Check URI length
                                        if len(uri) > 2048:
                                            warnings.append(f"Action {idx + 1}: URI very long ({len(uri)} chars)")
                                            print(f"        ⚠️  URI very long ({len(uri)} chars)")
                                        else:
                                            print(f"        ✅ URI length OK ({len(uri)} chars)")
                                    else:
                                        errors.append(f"Action {idx + 1}: URI must be string")
                                        print(f"        ❌ URI must be string")
                                else:
                                    errors.append(f"Action {idx + 1}: WebSocket endpoint requires 'uri' field")
                                    print(f"        ❌ Missing 'uri' field")
                                
                                # Check content-type
                                if 'content-type' in endpoint:
                                    content_type = endpoint['content-type']
                                    print(f"        ✅ Has 'content-type': '{content_type}'")
                                    
                                    # Validate audio format
                                    valid_formats = [
                                        'audio/l16;rate=16000',
                                        'audio/l16;rate=8000'
                                    ]
                                    if content_type in valid_formats:
                                        print(f"        ✅ Valid audio format")
                                    else:
                                        warnings.append(f"Action {idx + 1}: Unusual audio format '{content_type}'")
                                        print(f"        ⚠️  Unusual audio format")
                                else:
                                    warnings.append(f"Action {idx + 1}: Missing 'content-type' (recommended)")
                                    print(f"        ⚠️  Missing 'content-type' (recommended)")
                                
                                # Check for headers (optional)
                                if 'headers' in endpoint:
                                    print(f"        ✅ Has custom headers")
                                
                else:
                    errors.append(f"Action {idx + 1}: 'endpoint' must be array")
                    print(f"    ❌ 'endpoint' must be array")
            else:
                errors.append(f"Action {idx + 1}: 'connect' requires 'endpoint' field")
                print(f"    ❌ 'connect' requires 'endpoint' field")
    
    # Summary
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    
    if len(errors) == 0 and len(warnings) == 0:
        print("✅ NCCO is PERFECT! No errors or warnings.")
        print("🚀 Ready for production use!")
        return True
    
    if len(errors) > 0:
        print(f"\n❌ ERRORS FOUND ({len(errors)}):")
        for err in errors:
            print(f"   • {err}")
    
    if len(warnings) > 0:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"   • {warn}")
    
    if len(errors) == 0:
        print("\n✅ No critical errors - NCCO should work")
        print("⚠️  But warnings should be reviewed")
        return True
    else:
        print("\n❌ CRITICAL ERRORS - NCCO will be REJECTED by Vonage")
        return False

def test_websocket_format():
    """Test WebSocket URI format specifically"""
    print("\n" + "="*70)
    print("🔍 WEBSOCKET URI FORMAT TEST")
    print("="*70)
    
    test_uri = "wss://uncontortioned-na-ponderously.ngrok-free.dev/api/vonage-stream/TEST-UUID/"
    
    print(f"\n📍 Testing URI:")
    print(f"   {test_uri}")
    
    checks = []
    
    # Protocol
    if test_uri.startswith('wss://'):
        checks.append(("✅", "Secure WebSocket (wss://)"))
    elif test_uri.startswith('ws://'):
        checks.append(("⚠️ ", "Insecure WebSocket (ws://)"))
    else:
        checks.append(("❌", "Invalid protocol"))
    
    # Domain
    if 'ngrok-free.dev' in test_uri:
        checks.append(("✅", "Ngrok domain detected"))
    
    # Path
    if '/api/vonage-stream/' in test_uri:
        checks.append(("✅", "Correct API path"))
    
    # UUID placeholder
    if 'TEST-UUID' in test_uri or '{uuid}' in test_uri:
        checks.append(("✅", "UUID placeholder present"))
    
    # Length
    if len(test_uri) < 2048:
        checks.append(("✅", f"Length OK ({len(test_uri)}/2048 chars)"))
    else:
        checks.append(("❌", f"Too long ({len(test_uri)}/2048 chars)"))
    
    # No spaces
    if ' ' not in test_uri:
        checks.append(("✅", "No spaces in URI"))
    else:
        checks.append(("❌", "Contains spaces"))
    
    # Print results
    print("\n🔍 Checks:")
    for status, message in checks:
        print(f"   {status} {message}")
    
    all_passed = all(check[0] == "✅" for check in checks)
    
    print("\n" + "-"*70)
    if all_passed:
        print("✅ WebSocket URI format is VALID")
    else:
        print("⚠️  WebSocket URI has issues")
    
    return all_passed

def main():
    """Run all validations"""
    print("\n" + "="*70)
    print("🎯 VONAGE NCCO COMPLETE VALIDATION")
    print("="*70)
    print("This validates NCCO structure before making actual calls")
    print("="*70 + "\n")
    
    # Test 1: NCCO structure
    ncco_valid = validate_ncco_structure()
    
    # Test 2: WebSocket URI
    ws_valid = test_websocket_format()
    
    # Final verdict
    print("\n" + "="*70)
    print("🏁 FINAL VERDICT")
    print("="*70)
    
    if ncco_valid and ws_valid:
        print("✅ ALL VALIDATIONS PASSED!")
        print("🚀 NCCO is ready for real call testing")
        print("\n💡 Next step: Run test_realtime_call.py to initiate actual call")
        return True
    else:
        print("❌ VALIDATION FAILED!")
        print("🔧 Fix the issues above before making real calls")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
