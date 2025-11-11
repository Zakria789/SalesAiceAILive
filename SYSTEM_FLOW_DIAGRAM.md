# 🔄 System Flow: Database → HumeAI Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT CREATION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

1️⃣ USER CREATES AGENT
   │
   ├─ POST /api/agents/create/
   │  {
   │    "name": "Sales Agent",
   │    "sales_script_text": "Hi! I'm Sarah...",
   │    "business_info": {"company_name": "TechSolutions"},
   │    "knowledge_files": {"products": "AI Voice Agent"}
   │  }
   │
   ▼

2️⃣ AGENT SAVED TO DATABASE
   │
   ├─ Agent model fields:
   │  ✅ sales_script_text  = "Hi! I'm Sarah..."
   │  ✅ business_info      = {company_name: "TechSolutions"}
   │  ✅ knowledge_files    = {products: "AI Voice Agent"}
   │
   ▼

3️⃣ AUTO-SYNC WITH HUMEAI
   │
   ├─ hume_agent_service.create_agent(
   │     name="Sales Agent",
   │     system_prompt="You are...",
   │     agent_obj=agent  🔥 NEW!
   │  )
   │
   ▼

4️⃣ BUILD ENHANCED SYSTEM PROMPT
   │
   ├─ _build_system_prompt(agent_obj)
   │  │
   │  ├─ Base Prompt: "You are Sales Agent..."
   │  │
   │  ├─ + Sales Script from DB:
   │  │   "## SALES SCRIPT\nHi! I'm Sarah..."
   │  │
   │  ├─ + Business Info from DB:
   │  │   "## BUSINESS INFORMATION\nCompany: TechSolutions"
   │  │
   │  └─ + Knowledge Files from DB:
   │      "## KNOWLEDGE BASE\n- products: AI Voice Agent"
   │
   ▼

5️⃣ CREATE HUMEAI AGENT
   │
   ├─ POST https://api.hume.ai/v0/evi/configs
   │  {
   │    "name": "Sales Agent",
   │    "prompt": {
   │      "text": "[ENHANCED PROMPT WITH DB DATA]"
   │    }
   │  }
   │
   ▼

6️⃣ SAVE HUME CONFIG ID
   │
   ├─ agent.hume_config_id = "hume_abc123"
   │  agent.save()
   │
   ▼

✅ AGENT READY!


┌─────────────────────────────────────────────────────────────────┐
│                      CALL FLOW                                  │
└─────────────────────────────────────────────────────────────────┘

1️⃣ INCOMING CALL
   │
   ├─ Vonage WebSocket connects
   │  ws://your-domain/ws/vonage/call/{uuid}/
   │
   ▼

2️⃣ LOAD AGENT FROM DATABASE
   │
   ├─ call = TwilioCall.objects.get(call_sid=uuid)
   │  agent = call.agent
   │
   │  ✅ agent.sales_script_text
   │  ✅ agent.business_info
   │  ✅ agent.knowledge_files
   │
   ▼

3️⃣ GET DYNAMIC GREETING
   │
   ├─ _get_greeting_text()
   │  │
   │  ├─ Try: sales_script first line
   │  │   → "Hi! I'm Sarah from TechSolutions"
   │  │
   │  ├─ Try: business_info['greeting']
   │  │   → "Hello! Welcome to TechSolutions!"
   │  │
   │  ├─ Try: Build from company_name
   │  │   → "Hi! This is [Agent] from [Company]"
   │  │
   │  ├─ Try: Personalized for returning customer
   │  │   → "Hi John! Great to hear from you again!"
   │  │
   │  └─ Default: "Hi! How's it going?"
   │
   ▼

4️⃣ CONNECT TO HUMEAI
   │
   ├─ WebSocket to HumeAI EVI
   │  wss://api.hume.ai/v0/assistant/chat?config_id={agent.hume_config_id}
   │
   │  Session config:
   │  {
   │    "greeting": {
   │      "text": "[DYNAMIC GREETING FROM DB]" 🔥
   │    }
   │  }
   │
   ▼

5️⃣ CONVERSATION STARTS
   │
   ├─ Agent greets with DB greeting
   ├─ Agent follows DB sales script
   ├─ Agent uses DB knowledge base
   └─ Agent responds using all DB data
   │
   ▼

✅ CALL COMPLETED!


┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                 │
└─────────────────────────────────────────────────────────────────┘

DATABASE (agents_agent table)
│
├─ sales_script_text 📝
│  └─ Used in: System prompt + Greeting extraction
│
├─ business_info 🏢
│  └─ Used in: System prompt + Dynamic greeting
│
├─ knowledge_files 📚
│  └─ Used in: System prompt (knowledge base)
│
└─ hume_config_id 🤖
   └─ Links to: HumeAI EVI config

        ⬇️  ⬇️  ⬇️

HUMEAI (api.hume.ai)
│
├─ Enhanced System Prompt
│  ├─ Base prompt
│  ├─ + Sales script (from DB)
│  ├─ + Business info (from DB)
│  └─ + Knowledge files (from DB)
│
└─ Session Config
   └─ Dynamic greeting (from DB)

        ⬇️  ⬇️  ⬇️

CUSTOMER RECEIVES
│
├─ Personalized greeting 👋
├─ Relevant sales pitch 📝
├─ Accurate information 📚
└─ Natural conversation 💬


┌─────────────────────────────────────────────────────────────────┐
│                    BENEFITS                                     │
└─────────────────────────────────────────────────────────────────┘

✅ No Code Changes Needed
   └─ Update sales script in DB → Automatically used

✅ Per-Agent Customization
   └─ Each agent has own script & knowledge base

✅ Dynamic Content
   └─ Change greeting/script without redeploying

✅ Knowledge Management
   └─ Centralized in database, easy to update

✅ Personalization
   └─ Different greetings for new vs returning customers

✅ Easy Testing
   └─ Change DB → Test immediately → No server restart


┌─────────────────────────────────────────────────────────────────┐
│                    KEY FILES                                    │
└─────────────────────────────────────────────────────────────────┘

📁 agents/models.py
   └─ Agent model with sales_script_text, business_info fields

📁 HumeAiTwilio/hume_agent_service.py
   ├─ create_agent() - Accepts agent_obj parameter
   └─ _build_system_prompt() - Builds enhanced prompt from DB

📁 HumeAiTwilio/vonage_realtime_consumer.py
   └─ _get_greeting_text() - Gets dynamic greeting from DB

📁 agents/views.py
   └─ create_agent() - Passes agent_obj to HumeAI service


┌─────────────────────────────────────────────────────────────────┐
│                    EXAMPLE USAGE                                │
└─────────────────────────────────────────────────────────────────┘

# Create agent with DB fields
agent = Agent.objects.create(
    name='Sarah - Sales',
    sales_script_text='Hi! I\'m Sarah from TechSolutions...',
    business_info={'company_name': 'TechSolutions'},
    knowledge_files={'products': 'AI Voice Agent'}
)

# ✅ Auto-syncs with HumeAI
# ✅ agent.hume_config_id saved
# ✅ Enhanced prompt created with DB data

# On call:
# ✅ Greeting: "Hi! I'm Sarah from TechSolutions..."
# ✅ Agent follows sales_script_text
# ✅ Agent uses business_info knowledge
# ✅ Agent references knowledge_files


┌─────────────────────────────────────────────────────────────────┐
│                    STATUS: ✅ COMPLETE                          │
└─────────────────────────────────────────────────────────────────┘

Haan, main kar loonga! ✅

Agent ab database se:
✅ Sales script use karega
✅ Knowledge base use karega  
✅ Dynamic greeting use karega

Test karo: python test_db_sales_script_integration.py
```
