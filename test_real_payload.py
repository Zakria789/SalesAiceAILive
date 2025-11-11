"""
Test Create Agent with Real Frontend Payload
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.serializers import AgentCreateUpdateSerializer
from agents.models import Agent

User = get_user_model()

def test_create_agent_with_payload():
    """Test agent creation with real frontend payload"""
    
    print("\n" + "="*80)
    print("🧪 TESTING AGENT CREATION WITH FRONTEND PAYLOAD")
    print("="*80)
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    print(f"✅ Using user: {user.email}")
    
    # Real frontend payload
    payload = {
        'name': 'Sales For Testing 2',
        'agent_type': 'outbound',
        'status': 'active',
        'voice_tone': 'enthusiastic',
        'api_key_source': 'account_default',
        'hume_ai_config': {
            "enable_emotion_detection": True,
            "response_to_emotions": True,
            "sentiment_analysis": True,
            "emotion_models": ["prosody", "language"]
        },
        'sales_script_text': '''We specialize in harnessing the power of Artificial Intelligence and Automation to provide innovative, customized solutions for businesses across various industries. Our team of experienced developers is dedicated to helping you streamline processes, increase efficiency, and drive growth.

AI automation services by Coding The Brains are designed to help businesses streamline operations, enhance customer experiences, and leverage intelligent technologies. We specialize in chatbot development, machine learning (ML), data science solutions, and smart IoT system integrations that bring real impact.

From cutting-edge computer vision and deep learning models to custom application development, our expert team delivers scalable, AI-driven solutions tailored to your business needs.
At Coding The Brains, we deliver cutting-edge solutions leveraging AI and Machine Learning to predict trends, automate tasks, and augment decision-making. Our automation and bots streamline processes, saving time and resources. We harness Data Science to turn raw data into actionable insights for strategic advantage. We are also specialized in Computer Vision and Deep Learning, enhancing systems to interpret and understand the visual world. Our IoT solutions seamlessly integrate systems, fostering smooth data exchange and automation. Our focus lies in the intersection of technology and business, providing solutions that drive efficiency and growth.''',
        'operating_hours': {
            "start": "09:00",
            "end": "17:00",
            "timezone": "UTC",
            "working_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        },
        'auto_answer_enabled': False,
        'website_url': 'https://www.codingthebrains.com/',
        'campaign_schedule': {
            "name": "",
            "type": "immediate",
            "start_date": "",
            "max_calls_per_day": 100
        }
    }
    
    print(f"\n📋 Payload Summary:")
    print(f"   Name: {payload['name']}")
    print(f"   Type: {payload['agent_type']}")
    print(f"   Sales Script: {len(payload['sales_script_text'])} chars")
    print(f"   Website: {payload['website_url']}")
    
    # Test serializer
    print(f"\n🔹 STEP 1: Testing Serializer Validation...")
    
    serializer = AgentCreateUpdateSerializer(
        data=payload,
        context={'request': type('obj', (object,), {'user': user})()}
    )
    
    if serializer.is_valid():
        print(f"✅ Serializer validation passed")
        print(f"\n📊 Validated Data:")
        for key, value in serializer.validated_data.items():
            if key == 'sales_script_text':
                print(f"   {key}: {len(value)} chars")
            elif isinstance(value, dict):
                print(f"   {key}: {json.dumps(value, indent=6)}")
            else:
                print(f"   {key}: {value}")
    else:
        print(f"❌ Serializer validation failed:")
        print(json.dumps(serializer.errors, indent=2))
        return
    
    # Create agent
    print(f"\n🔹 STEP 2: Creating Agent in Database...")
    
    try:
        # Add owner manually since we're bypassing the view
        agent = serializer.save(owner=user)
        
        print(f"✅ Agent created successfully!")
        print(f"\n📋 Agent Details:")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Type: {agent.agent_type}")
        print(f"   Status: {agent.status}")
        print(f"   Sales Script: {len(agent.sales_script_text) if agent.sales_script_text else 0} chars")
        print(f"   Website: {agent.website_url}")
        print(f"   Voice Tone: {agent.voice_tone}")
        
        # Check if sales_script_text was saved
        if agent.sales_script_text:
            print(f"\n✅ Sales Script Saved Successfully!")
            print(f"   Preview (first 200 chars):")
            print("-" * 80)
            print(agent.sales_script_text[:200] + "...")
            print("-" * 80)
        else:
            print(f"\n❌ Sales Script NOT saved!")
        
        # Sync to HumeAI
        print(f"\n🔹 STEP 3: Syncing to HumeAI...")
        
        try:
            from HumeAiTwilio.hume_agent_service import hume_agent_service
            
            config_id = hume_agent_service.create_agent(
                name=agent.name,
                system_prompt=f"You are {agent.name}, an AI sales assistant for Coding The Brains.",
                voice_name='Ito',
                language='en',
                agent_obj=agent
            )
            
            if config_id:
                agent.hume_config_id = config_id
                agent.save(update_fields=['hume_config_id'])
                print(f"✅ HumeAI sync successful!")
                print(f"   Config ID: {config_id}")
            else:
                print(f"❌ HumeAI sync failed (no config_id returned)")
                
        except Exception as hume_error:
            print(f"❌ HumeAI sync error: {hume_error}")
            import traceback
            traceback.print_exc()
        
        # Final verification
        print(f"\n🔹 STEP 4: Final Verification...")
        agent.refresh_from_db()
        
        print(f"✅ Agent in Database:")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   HumeAI Config ID: {agent.hume_config_id or '❌ Not synced'}")
        print(f"   Sales Script: {'✅ ' + str(len(agent.sales_script_text)) + ' chars' if agent.sales_script_text else '❌ Empty'}")
        
        # Check HumeAI
        if agent.hume_config_id:
            print(f"\n🔍 Checking HumeAI Config...")
            try:
                hume_agent = hume_agent_service.get_agent(agent.hume_config_id)
                
                if hume_agent:
                    prompt_text = hume_agent.get('prompt', {}).get('text', '')
                    print(f"✅ Found in HumeAI")
                    print(f"   Prompt Length: {len(prompt_text)} chars")
                    
                    # Check if sales script is in prompt
                    if agent.sales_script_text and agent.sales_script_text[:100] in prompt_text:
                        print(f"   ✅ Sales Script INCLUDED in HumeAI prompt")
                    elif 'Coding The Brains' in prompt_text:
                        print(f"   ⚠️  Sales Script partially included")
                    else:
                        print(f"   ❌ Sales Script NOT FOUND in HumeAI prompt")
                    
                    print(f"\n📝 HumeAI Prompt Preview (first 500 chars):")
                    print("-" * 80)
                    print(prompt_text[:500] + "...")
                    print("-" * 80)
                else:
                    print(f"❌ Not found in HumeAI")
                    
            except Exception as e:
                print(f"❌ Error fetching from HumeAI: {e}")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80)
        
        # Cleanup
        cleanup = input("\n🗑️  Delete test agent? (y/n): ").strip().lower()
        if cleanup == 'y':
            if agent.hume_config_id:
                try:
                    hume_agent_service.delete_agent(agent.hume_config_id)
                    print(f"✅ Deleted from HumeAI")
                except:
                    pass
            agent.delete()
            print(f"✅ Deleted from database")
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_agent_with_payload()
