"""
Test Serializer Fields - Check what fields are accepted
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.serializers import AgentCreateUpdateSerializer

def test_serializer_fields():
    """Check which fields the serializer accepts"""
    
    print("\n" + "="*80)
    print("🧪 TESTING SERIALIZER FIELDS")
    print("="*80)
    
    serializer = AgentCreateUpdateSerializer()
    
    print(f"\n📋 Fields accepted by AgentCreateUpdateSerializer:")
    print("-" * 80)
    
    for field_name in serializer.fields.keys():
        field = serializer.fields[field_name]
        field_type = type(field).__name__
        required = field.required
        
        status = "✅ Required" if required else "⚪ Optional"
        print(f"   {status} | {field_name:30} | Type: {field_type}")
    
    print("-" * 80)
    print(f"\n✅ Total fields: {len(serializer.fields)}")
    
    # Check specific fields
    print(f"\n🔍 Key Fields Check:")
    print(f"   sales_script_text: {'✅ Present' if 'sales_script_text' in serializer.fields else '❌ Missing'}")
    print(f"   sales_script_file: {'✅ Present' if 'sales_script_file' in serializer.fields else '❌ Missing'}")
    print(f"   business_info: {'✅ Present' if 'business_info' in serializer.fields else '❌ Missing'}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_serializer_fields()
