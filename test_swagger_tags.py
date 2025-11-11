#!/usr/bin/env python3
"""
Test script to verify Swagger schema has only official tags without duplicates
"""
import requests
import json

def test_swagger_schema():
    """Test that Swagger schema only contains official tags"""
    print("🔍 Testing Swagger Schema Tags...")
    
    try:
        # Get the OpenAPI schema JSON
        response = requests.get('http://127.0.0.1:8000/swagger/?format=openapi')
        response.raise_for_status()
        
        schema = response.json()
        
        # Extract tags from schema
        tags = []
        if 'tags' in schema:
            tags = [tag['name'] if isinstance(tag, dict) else str(tag) for tag in schema['tags']]
        
        print(f"📋 Found tags in schema: {tags}")
        
        # Define expected official tags
        expected_tags = {
            'Dashboard',
            'Authentication', 
            'User Management',
            'Subscriptions',
            'AI Agents',
            'Calls'
        }
        
        # Check for duplicates
        unique_tags = set(tags)
        duplicates = len(tags) - len(unique_tags)
        
        if duplicates > 0:
            print(f"❌ Found {duplicates} duplicate tags!")
            print(f"   All tags: {tags}")
            print(f"   Unique tags: {list(unique_tags)}")
        else:
            print("✅ No duplicate tags found!")
        
        # Check if we have all expected tags
        missing_tags = expected_tags - unique_tags
        extra_tags = unique_tags - expected_tags
        
        if missing_tags:
            print(f"⚠️  Missing expected tags: {missing_tags}")
        
        if extra_tags:
            print(f"⚠️  Found unexpected tags: {extra_tags}")
        
        if not missing_tags and not extra_tags and duplicates == 0:
            print("🎉 SUCCESS: Swagger schema has exactly the expected 6 tags without duplicates!")
        else:
            print("❌ ISSUE: Schema doesn't match expected format")
        
        # Also check paths for tag consistency
        path_tags = set()
        if 'paths' in schema:
            for path, methods in schema['paths'].items():
                for method, operation in methods.items():
                    if isinstance(operation, dict) and 'tags' in operation:
                        for tag in operation['tags']:
                            path_tags.add(tag)
        
        print(f"📊 Tags found in API paths: {sorted(path_tags)}")
        
        # Check if path tags match schema tags
        path_extra = path_tags - unique_tags
        if path_extra:
            print(f"⚠️  Path tags not in schema: {path_extra}")
        else:
            print("✅ All path tags are consistent with schema tags!")
            
        return len(missing_tags) == 0 and len(extra_tags) == 0 and duplicates == 0
        
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        return False

if __name__ == '__main__':
    success = test_swagger_schema()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Swagger schema test {'passed' if success else 'failed'}!")
