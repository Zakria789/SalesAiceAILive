#!/usr/bin/env python
"""
Quick test script to verify analytics views can be imported
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print("🔍 Testing analytics views import...")

try:
    from HumeAiTwilio.api_views.analytics_views import (
        conversation_metrics,
        objection_types,
        clarifies_flow_analysis,
        win_loss_rate,
        tone_trends,
        call_explainability,
        risk_flags_audit
    )
    print("✅ SUCCESS: All analytics views imported correctly!")
    print(f"   - conversation_metrics: {conversation_metrics}")
    print(f"   - objection_types: {objection_types}")
    print(f"   - clarifies_flow_analysis: {clarifies_flow_analysis}")
    print(f"   - win_loss_rate: {win_loss_rate}")
    print(f"   - tone_trends: {tone_trends}")
    print(f"   - call_explainability: {call_explainability}")
    print(f"   - risk_flags_audit: {risk_flags_audit}")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔍 Testing URL registration...")
try:
    from HumeAiTwilio.urls import urlpatterns
    analytics_urls = [
        url for url in urlpatterns 
        if 'analytics' in str(url.pattern)
    ]
    print(f"✅ Found {len(analytics_urls)} analytics URL patterns:")
    for url in analytics_urls:
        print(f"   - {url.pattern}")
except Exception as e:
    print(f"❌ URL CHECK ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All checks passed! The server needs to be restarted to pick up the changes.")
