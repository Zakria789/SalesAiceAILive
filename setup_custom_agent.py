"""
🤖 CUSTOM AGENT IMPLEMENTATION EXAMPLE
Apna agent kaise banatey hain - Step by step code

Run this file to automatically setup your custom agent with training
"""

import os
import sys
import json
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
sys.path.insert(0, '/e/Python-AI/Django-Backend/TESTREPO')

try:
    django.setup()
except:
    print("⚠️ Django setup issue - running in simulation mode")

from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Create Custom Agent Model Definition
# ═══════════════════════════════════════════════════════════════════════════════

CUSTOM_AGENT_MODEL = """
# Add this to your agents/models.py:

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CustomAIAgent(models.Model):
    '''Your own trained AI agent - completely in your control'''
    
    AGENT_TYPE_CHOICES = [
        ('sales', 'Sales Calls'),
        ('support', 'Support Calls'),
        ('followup', 'Follow-up Calls'),
        ('survey', 'Survey Calls'),
        ('retention', 'Retention Calls'),
    ]
    
    STATUS_CHOICES = [
        ('training', 'Training Phase'),
        ('trained', 'Ready for Calls'),
        ('active', 'Making Calls'),
        ('learning', 'Learning from Data'),
        ('optimizing', 'Optimizing Performance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_ai_agent')
    
    # Basic Info
    name = models.CharField(max_length=100, default='My Custom Agent')
    description = models.TextField(blank=True)
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPE_CHOICES, default='sales')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    
    # System Configuration
    system_prompt = models.TextField(
        default='You are a helpful sales assistant',
        help_text='How your agent should behave'
    )
    
    # Agent's Brain - Knowledge Base
    knowledge_base = models.JSONField(
        default=dict,
        help_text='All training data (scripts, objections, product info)'
    )
    
    # Learning & Performance
    learning_data = models.JSONField(default=dict)
    calls_made = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_called = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'custom_ai_agents'
        verbose_name = 'Custom AI Agent'
        verbose_name_plural = 'Custom AI Agents'
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def update_success_rate(self):
        '''Calculate success rate'''
        if self.calls_made > 0:
            self.success_rate = (self.successful_calls / self.calls_made) * 100
            self.save()
    
    def add_learning(self, learning_entry):
        '''Add new learning from a call'''
        if 'interactions' not in self.learning_data:
            self.learning_data['interactions'] = []
        
        self.learning_data['interactions'].append(learning_entry)
        
        # Keep only last 1000 interactions
        if len(self.learning_data['interactions']) > 1000:
            self.learning_data['interactions'] = self.learning_data['interactions'][-1000:]
        
        self.save()
"""

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Create Training Data
# ═══════════════════════════════════════════════════════════════════════════════

class TrainingDataCreator:
    """Create comprehensive training data for your agent"""
    
    @staticmethod
    def create_sales_training():
        """Complete training data for sales agent"""
        
        training = {
            # ─────────────────────────────────────────────────────
            # SALES SCRIPTS (Opening lines)
            # ─────────────────────────────────────────────────────
            "sales_scripts": [
                "Hi, this is [Agent] from [Company]. Do you have 30 seconds?",
                "I'm calling because we help companies like yours save time with [Product].",
                "Quick question - are you currently using [ProductType]?",
                "I hope I'm not catching you at a bad time. This should only take a minute.",
                "We just helped a company similar to yours increase efficiency by 40%. Can we discuss?"
            ],
            
            # ─────────────────────────────────────────────────────
            # OBJECTION RESPONSES (How to handle objections)
            # ─────────────────────────────────────────────────────
            "objection_responses": {
                "too_expensive": [
                    "I understand cost is important. What if I could show you how to save 20% monthly?",
                    "Many clients initially had the same concern. Our ROI is typically 300% in 3 months.",
                    "Let me ask - what's your annual budget for this type of solution?"
                ],
                "not_interested": [
                    "That's fair. Can I ask what you're currently using instead?",
                    "I respect that. What would have to change for this to be relevant to you?",
                    "No pressure. Can I send you information for future reference?"
                ],
                "thinking_about_it": [
                    "Smart to consider carefully. What specific information would help your decision?",
                    "What are your main concerns right now?",
                    "When would be a good time to follow up with you?"
                ],
                "call_me_later": [
                    "Absolutely. What day and time work best for you?",
                    "Perfect. I'll call you [day] at [time]. Is that still good?",
                    "Great. Should I reach you at this number?"
                ],
                "send_email": [
                    "Happy to! What email should I send it to?",
                    "I'll email information right now. What's the best email for you?",
                    "You'll get it in a few minutes. Watch for our message."
                ],
            },
            
            # ─────────────────────────────────────────────────────
            # PRODUCT INFORMATION
            # ─────────────────────────────────────────────────────
            "product_info": {
                "name": "Your Product Name",
                "tagline": "One-line description of your product",
                "description": "Detailed description of what your product does",
                "features": [
                    "Feature 1 - What it does",
                    "Feature 2 - What it does",
                    "Feature 3 - What it does",
                ],
                "benefits": [
                    "Benefit 1 - Save 40+ hours weekly",
                    "Benefit 2 - Increase efficiency by 300%",
                    "Benefit 3 - Reduce costs by 25%",
                ],
                "pricing": {
                    "basic": "$299/month",
                    "pro": "$599/month",
                    "enterprise": "Custom pricing"
                },
                "target_industries": ["Tech", "E-commerce", "SaaS", "Agencies"],
                "ideal_customer": "Companies with 5-500 employees",
            },
            
            # ─────────────────────────────────────────────────────
            # CONVERSATION RULES (How to respond)
            # ─────────────────────────────────────────────────────
            "conversation_rules": [
                {
                    "trigger": "budget",
                    "response": "Price is flexible. We work with companies of all sizes.",
                    "intent": "Address price concerns"
                },
                {
                    "trigger": "timeline",
                    "response": "Implementation takes just 2 days. You'll see results immediately.",
                    "intent": "Address timeline concerns"
                },
                {
                    "trigger": "security",
                    "response": "We're SOC 2 certified with 99.9% uptime SLA.",
                    "intent": "Build trust"
                },
            ],
            
            # ─────────────────────────────────────────────────────
            # AGENT PERSONALITY
            # ─────────────────────────────────────────────────────
            "personality": {
                "tone": "Professional but friendly",
                "communication_style": "Consultative, not pushy",
                "speed": "Conversational pace",
                "empathy_level": "High - listen first, sell second",
                "closing_style": "Soft close - ask for next step"
            },
            
            # ─────────────────────────────────────────────────────
            # SUCCESS INDICATORS
            # ─────────────────────────────────────────────────────
            "success_indicators": {
                "demo_booked": 5,
                "interest_shown": 3,
                "need_more_info": 2,
                "call_back_scheduled": 4,
            }
        }
        
        return training


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Response Generation Engine
# ═══════════════════════════════════════════════════════════════════════════════

class CustomAgentResponseEngine:
    """Generate intelligent responses from training data"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def generate_response(self, customer_message):
        """
        Generate best response based on customer message
        """
        
        customer_msg_lower = customer_message.lower()
        
        # STEP 1: Identify message type
        objections = self.kb.get('objection_responses', {})
        
        for objection_key, responses in objections.items():
            if objection_key.lower() in customer_msg_lower:
                # Found matching objection
                return {
                    'response': responses[0],  # Use first response
                    'type': f'objection_{objection_key}',
                    'confidence': 0.95
                }
        
        # STEP 2: Check for product questions
        if any(word in customer_msg_lower for word in ['features', 'price', 'cost', 'benefit', 'how']):
            product = self.kb.get('product_info', {})
            features = product.get('features', [])
            if features:
                return {
                    'response': f"Great question! Our key features include {features[0]}. Let me tell you more.",
                    'type': 'product_info',
                    'confidence': 0.85
                }
        
        # STEP 3: Check conversation rules
        rules = self.kb.get('conversation_rules', [])
        for rule in rules:
            if rule['trigger'].lower() in customer_msg_lower:
                return {
                    'response': rule['response'],
                    'type': 'rule_based',
                    'confidence': 0.80
                }
        
        # STEP 4: Default response
        return {
            'response': "Tell me more about that.",
            'type': 'generic',
            'confidence': 0.50
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Complete Setup Function
# ═══════════════════════════════════════════════════════════════════════════════

def setup_custom_agent_complete():
    """
    Complete automatic setup of custom agent
    Ek command se pura agent ready ho jaye
    """
    
    print("\\n" + "="*80)
    print("🤖 CUSTOM AI AGENT SETUP")
    print("="*80)
    
    try:
        # Get user
        user = User.objects.first()
        if not user:
            print("❌ No user found. Create a user first.")
            return None
        
        print(f"\\n👤 User: {user.email}")
        
        # Create training data
        print("\\n📚 Creating training data...")
        trainer = TrainingDataCreator()
        training_data = trainer.create_sales_training()
        
        print(f"   ✅ Sales scripts: {len(training_data['sales_scripts'])}")
        print(f"   ✅ Objections: {len(training_data['objection_responses'])}")
        print(f"   ✅ Product info: Complete")
        
        # Create or get agent
        print("\\n🤖 Creating agent...")
        try:
            from agents.models import CustomAIAgent
            
            agent, created = CustomAIAgent.objects.get_or_create(
                user=user,
                defaults={
                    'name': f"{user.first_name or 'Custom'} AI Agent",
                    'agent_type': 'sales',
                    'status': 'training',
                }
            )
            
            status_text = "CREATED" if created else "LOADED"
            print(f"   ✅ Agent {status_text}: {agent.name}")
        
        except ImportError:
            print("   ⚠️ CustomAIAgent model not found. Create it first.")
            print("   📝 Run migration: python manage.py migrate")
            return None
        
        # Train the agent
        print("\\n🎓 Training agent with data...")
        agent.knowledge_base = training_data
        agent.system_prompt = """You are a professional sales agent trained in consultative selling.
Your role is to:
1. Build rapport and trust with customers
2. Understand their needs through listening
3. Present relevant solutions
4. Handle objections diplomatically
5. Secure next meeting or commitment

Always be respectful, patient, and focus on customer value."""
        
        agent.status = 'trained'
        agent.save()
        
        print("   ✅ Knowledge base updated")
        print("   ✅ System prompt configured")
        print("   ✅ Status: TRAINED")
        
        # Display final status
        print("\\n" + "─"*80)
        print("📊 AGENT STATUS")
        print("─"*80)
        print(f"   Name: {agent.name}")
        print(f"   Type: {agent.agent_type}")
        print(f"   Status: {agent.status}")
        print(f"   Training Data Size: {len(json.dumps(agent.knowledge_base)) / 1024:.1f} KB")
        print(f"   Sales Scripts: {len(training_data['sales_scripts'])}")
        print(f"   Objection Responses: {len(training_data['objection_responses'])}")
        print(f"   Calls Made: {agent.calls_made}")
        print(f"   Success Rate: {agent.success_rate:.1f}%")
        
        print("\\n" + "="*80)
        print("✅ AGENT READY FOR DEPLOYMENT!")
        print("="*80)
        
        return agent
    
    except Exception as e:
        print(f"\\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Test Response Generation
# ═══════════════════════════════════════════════════════════════════════════════

def test_agent_responses():
    """Test how the agent responds to different inputs"""
    
    print("\\n" + "="*80)
    print("🧪 TESTING AGENT RESPONSES")
    print("="*80)
    
    trainer = TrainingDataCreator()
    training_data = trainer.create_sales_training()
    
    engine = CustomAgentResponseEngine(training_data)
    
    # Test cases
    test_messages = [
        "This is too expensive",
        "I'm not interested",
        "What are your features?",
        "How much does it cost?",
        "I'm thinking about it",
        "Can you send me information?",
        "I need to check my budget",
    ]
    
    print("\\n📞 Testing customer messages:\\n")
    
    for msg in test_messages:
        response = engine.generate_response(msg)
        
        print(f"Customer: {msg}")
        print(f"  Agent: {response['response']}")
        print(f"  Type: {response['type']} | Confidence: {response['confidence']:.0%}\\n")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    
    print("\\n🚀 CUSTOM AGENT SETUP SCRIPT")
    print("="*80)
    
    # Show model definition
    print("\\n1️⃣ MODEL DEFINITION:")
    print("   Add this to agents/models.py:")
    print("   " + CUSTOM_AGENT_MODEL[:200] + "...")
    
    # Test response generation (works without Django)
    print("\\n2️⃣ TESTING RESPONSE GENERATION:")
    test_agent_responses()
    
    # Setup agent (requires Django)
    print("\\n3️⃣ SETTING UP AGENT:")
    try:
        agent = setup_custom_agent_complete()
        
        if agent:
            print("\\n✅ SUCCESS! Your custom agent is ready.")
            print(f"   Agent ID: {agent.id}")
            print("\\n📝 Next Steps:")
            print("   1. Integrate with Twilio for calls")
            print("   2. Create response API endpoint")
            print("   3. Start making calls")
            print("   4. Monitor learning & improvements")
    
    except Exception as e:
        print(f"\\n⚠️ Django setup issue: {str(e)}")
        print("   Run this with: python manage.py shell < setup_custom_agent.py")
