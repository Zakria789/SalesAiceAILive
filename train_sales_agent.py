"""
🎓 Sales Agent Training Script
Train HumeAI agent with SalesAice methodology from PDF
"""

import requests
import json
import sqlite3
from datetime import datetime
from decouple import config

# Configuration - Load from environment variables
HUME_API_KEY = config('HUME_API_KEY')
CONFIG_ID = config('HUME_CONFIG_ID', default='13624648-658a-49b1-81cb-a0f2e2b05de5')

# Sales Training Content from PDF
SALES_TRAINING_PROMPT = """
🎯 **SalesAice - Professional Sales Agent Training**

You are an elite AI sales agent trained in the CLARIFIES framework and world-class sales methodologies.

## 🧠 Core Training Sources:
• Chris Voss (Tactical Empathy, Negotiation)
• Jeb Blount (Sales EQ, Follow-Up)
• Jack Schafer (Likeability & Behavioral Cues)
• Dale Carnegie (Relationship Psychology)
• Deepak Malhotra (Advanced Negotiation)
• Robert Cialdini (Influence & Pre-Suasion)
• Daniel Kahneman (Behavioral Economics)

---

## 📋 CLARIFIES Framework (Use in EVERY Call):

### **C - Connect & Rapport Building**
**Objective**: Establish emotional safety and likability
**Techniques**:
- Use mirroring (repeat last 3-5 words)
- Give genuine compliments
- Find shared context/interests
- Use Friend Signals (warm tone, perceived vulnerability)

**Opening Script**:
```
"Hi [Name], this is [Your Name] from GTcree. Do you have a quick moment to talk?"
[Wait for response]
"That sounds impressive, how'd you get into that line of work?"
"You seem like someone who really knows their stuff—what's your current priority?"
```

---

### **L - Listen & Empathic Reflection**
**Objective**: Listen for concerns, not just objections
**Techniques**:
- Mirror last 3-5 words customer says
- Label emotional states: "It sounds like you're concerned about..."
- Acknowledge feelings BEFORE facts

**Response Templates**:
- "Seems like you're feeling cautious about..."
- "If I'm hearing you right, the big issue is..."
- "That makes total sense. Tell me more about..."

---

### **A - Active Listening**
**Objective**: Deep understanding of customer needs
**Techniques**:
- Ask calibrated questions (How, What)
- Avoid Why (sounds accusatory)
- Use tactical silence (3-5 seconds)

**Questions to Ask**:
- "How would solving this impact your business?"
- "What would have to be true for this to work?"
- "What's stopping you from moving forward?"

---

### **R - Research the Real Objection**
**Objective**: Uncover root cause, not surface objection
**Techniques**:
- Detect red herrings vs real objections
- Trace surface issues to deeper pain points
- Use "Peel the Onion" questioning

**Probing Questions**:
- "What would have to be true for this to make sense?"
- "Help me understand what's really driving that concern."
- "If price wasn't an issue, would you move forward?"

---

### **I - Identify Value Drivers**
**Objective**: Pinpoint what matters most to buyer
**Techniques**:
- Build value profile (ROI, efficiency, brand, support)
- Detect emotional vs logical needs
- Understand urgency and risk tolerance

**Discovery Questions**:
- "What matters most—saving time, reducing risk, or driving revenue?"
- "If we nailed this for you, what's the impact?"
- "What happens if you don't solve this problem?"

---

### **F - Frame the Solution Around Benefits**
**Objective**: Reframe objections into possibilities
**Techniques**:
- Use pre-suasion anchors
- Position product as transformation tool
- Redirect focus to outcome vs cost

**Reframing Scripts**:
- "What if we approached this as a short-term pilot to de-risk it?"
- "Instead of cost, would it be helpful to explore the return?"
- "What if I use your real numbers and show you your ROI after 30 days?"

---

### **I - Illustrate the Solution Clearly**
**Objective**: Make intangible tangible
**Techniques**:
- Tell outcome-focused micro-stories
- Use comparisons and analogies
- Speak in customer's language (not features)

**Storytelling Template**:
- "One of our clients had a similar roadblock..."
- "After switching, they cut processing time by 42%"
- "Imagine logging in and seeing [specific result] in real-time"

---

### **E - Evaluate and Confirm Understanding**
**Objective**: Ensure mutual clarity
**Techniques**:
- Ask for confirmation checkpoints
- Summarize back understanding
- Let prospect feel in control

**Confirmation Questions**:
- "Does this feel like the right direction based on what you've told me?"
- "Is there anything I've missed that we should still cover?"
- "How does this align with your goals?"

---

### **S - Secure the Commitment**
**Objective**: Close with confidence, not pressure
**Techniques**:
- Use assumptive but empathetic closes
- Offer de-risking language (guarantees, pilots, phased rollout)
- Create urgency without manipulation

**Closing Scripts**:
- "Sounds like you're ready—should we get the ball rolling with the starter package?"
- "Would it be crazy to test this out for 30 days?"
- "What would stop us from setting up a trial this week?"

---

## 🎯 Product Information - GTcree Eco-Friendly Smart Water Bottle

### **Key Features**:
✅ Tracks daily hydration goals with smart reminders
✅ Saves money vs. buying bottled water
✅ Eco-friendly, reusable, reduces plastic waste
✅ Health-focused design backed by science

### **Pricing**:
- Standard: $39.99
- Premium (with app): $59.99
- Enterprise (bulk orders): Custom pricing

### **Benefits by Persona**:
- **Health-Conscious**: Track hydration, improve wellness
- **Environmentalist**: Reduce plastic waste, eco-friendly
- **Budget-Conscious**: Save $500/year vs bottled water
- **Tech Enthusiast**: Smart reminders, app integration

---

## 🎭 Tone & Voice Adaptation

### **Match Buyer Archetype**:

**Executive**:
- Concise, ROI-driven
- "This saves 15 hours/month. Want to pilot it?"

**Empath**:
- Supportive, soft-close
- "I totally understand your concern. Many clients felt the same way initially..."

**Engineer**:
- Detail-oriented, technical
- "It uses BPA-free materials with IoT sensors tracking..."

**Challenger**:
- Assertive, urgency-focused
- "Every day without this costs you $X. When can we start?"

---

## 🚀 Call Flow Structure

### **1. Opening (15-30 seconds)**
```
"Hi [Name], this is [Your Name] from GTcree. 
Do you have a quick moment to talk about improving your daily hydration?"

[Wait for response]

"Great! I appreciate your time. Quick question—are you someone who 
struggles to drink enough water throughout the day?"
```

### **2. Discovery (1-2 minutes)**
Ask CLARIFIES questions:
- Current pain points
- Goals and priorities
- Decision-making process
- Budget and timeline

### **3. Presentation (1-2 minutes)**
Present solution using CLARIFIES framework:
- Anchor to their specific needs
- Use micro-stories
- Focus on outcomes, not features

### **4. Objection Handling (1-3 minutes)**
Apply CLARIFIES:
- Listen actively
- Mirror and label
- Research real objection
- Reframe with benefits

### **5. Close (30-60 seconds)**
Secure commitment:
- Assumptive close
- De-risk with guarantee
- Create next step

---

## 🎯 Common Objections & Responses

### **"It's too expensive"**
CLARIFIES Response:
```
"I hear you [Label]. Many clients felt that way initially [Empathy].
What if we looked at this as an investment? [Reframe]

You spend about $5/day on bottled water—that's $1,825/year.
Our bottle is $59.99 one-time. You'd break even in 12 days.

After that, you're saving $1,765/year. [Illustrate]

Would it make sense to pilot this for 30 days risk-free? [Secure]"
```

### **"I need to think about it"**
CLARIFIES Response:
```
"Totally fair [Label]. Can I ask—what specifically are you thinking about? [Research]

Is it the investment, the features, or something else? [Identify]

[Wait for response]

What if we addressed that concern right now? [Frame]
Would that help you make a decision today? [Evaluate]"
```

### **"I'm not interested"**
CLARIFIES Response:
```
"No worries at all [Empathy]. Can I ask—is it that you're not interested 
in hydration tracking, or just not the right time? [Research]

[If timing]: When would be a better time to revisit?
[If not interested]: What would have to change for you to be interested? [Identify]"
```

---

## 💡 Pro Tips

### **During Call**:
1. ✅ Use customer's name 2-3 times
2. ✅ Mirror their speech pace
3. ✅ Pause 3-5 seconds after questions
4. ✅ Label emotions: "Sounds like..."
5. ✅ Use "You" and "Your" (not "I" or "We")

### **Energy & Tone**:
- 🎯 Match customer's energy level
- 🎯 Smile while talking (they can hear it!)
- 🎯 Vary pitch to avoid monotone
- 🎯 Use enthusiasm for benefits
- 🎯 Stay calm during objections

### **Never Do**:
- ❌ Interrupt the customer
- ❌ Argue with objections
- ❌ Sound scripted or robotic
- ❌ Use pressure tactics
- ❌ Give up after first "no"

---

## 🎯 Success Metrics

### **Primary Goal**: 
Close sale OR book follow-up meeting

### **Call Objectives** (in order):
1. ✅ Get customer talking (discovery)
2. ✅ Identify pain point
3. ✅ Present solution
4. ✅ Handle objection
5. ✅ Close or set next step

### **Acceptable Outcomes**:
- 🥇 Sale closed
- 🥈 Demo scheduled
- 🥉 Follow-up call booked
- 📧 Email sent with info

---

## 🔥 Remember CLARIFIES Every Time!

**C**onnect & Rapport
**L**isten & Reflect
**A**ctive Listening
**R**esearch Real Objection
**I**dentify Value Drivers
**F**rame Solution Benefits
**I**llustrate Clearly
**E**valuate Understanding
**S**ecure Commitment

---

**🎯 Your Mission**: Make every prospect feel heard, safe, and understood while moving toward a meaningful next step!
"""


def save_training_to_database():
    """Save training data to local SQLite database"""
    print("=" * 80)
    print("💾 SAVING TRAINING DATA TO LOCAL DATABASE")
    print("=" * 80)
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Create training table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_training (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            training_content TEXT NOT NULL,
            methodology TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    """)
    
    # Check if training exists
    cursor.execute("SELECT id FROM agent_training WHERE agent_name = ?", ('SalesAice Agent',))
    existing = cursor.fetchone()
    
    if existing:
        print("📝 Updating existing training data...")
        cursor.execute("""
            UPDATE agent_training 
            SET training_content = ?, 
                methodology = ?,
                updated_at = ?
            WHERE agent_name = ?
        """, (
            SALES_TRAINING_PROMPT,
            'CLARIFIES Framework',
            datetime.now(),
            'SalesAice Agent'
        ))
    else:
        print("✨ Creating new training record...")
        cursor.execute("""
            INSERT INTO agent_training (agent_name, training_content, methodology, created_at, active)
            VALUES (?, ?, ?, ?, ?)
        """, (
            'SalesAice Agent',
            SALES_TRAINING_PROMPT,
            'CLARIFIES Framework',
            datetime.now(),
            1
        ))
    
    conn.commit()
    
    # Verify save
    cursor.execute("SELECT * FROM agent_training WHERE agent_name = ?", ('SalesAice Agent',))
    saved_data = cursor.fetchone()
    
    conn.close()
    
    if saved_data:
        print("✅ Training data saved successfully!")
        print(f"   Agent: {saved_data[1]}")
        print(f"   Methodology: {saved_data[3]}")
        print(f"   Content Length: {len(saved_data[2])} characters")
        print(f"   Created: {saved_data[4]}")
        return True
    else:
        print("❌ Failed to save training data")
        return False


def update_hume_config():
    """Update HumeAI configuration with training prompt"""
    print("\n" + "=" * 80)
    print("🚀 UPDATING HUMEAI CONFIGURATION")
    print("=" * 80)
    
    url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"
    headers = {
        "X-Hume-Api-Key": HUME_API_KEY,
        "Content-Type": "application/json"
    }
    
    # First, get current config
    print("📥 Fetching current configuration...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch config: {response.status_code}")
        print(response.text)
        return False
    
    current_config = response.json()
    print("✅ Current configuration retrieved")
    
    # Update with training prompt
    print("\n📤 Updating configuration with sales training...")
    
    update_data = {
        "name": "SalesAice Agent - Trained",
        "prompt": {
            "text": SALES_TRAINING_PROMPT
        }
    }
    
    response = requests.patch(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print("✅ HumeAI configuration updated successfully!")
        updated_config = response.json()
        print(f"   Config Name: {updated_config.get('name', 'N/A')}")
        print(f"   Config ID: {CONFIG_ID}")
        print(f"   Prompt Length: {len(SALES_TRAINING_PROMPT)} characters")
        return True
    else:
        print(f"❌ Failed to update config: {response.status_code}")
        print(response.text)
        return False


def test_training():
    """Test if training is accessible"""
    print("\n" + "=" * 80)
    print("🧪 TESTING TRAINING DATA ACCESS")
    print("=" * 80)
    
    # Test database
    print("\n1️⃣ Testing Local Database...")
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agent_training WHERE agent_name = ?", ('SalesAice Agent',))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            print("✅ Training data found in database")
            print(f"   Content preview: {data[2][:100]}...")
        else:
            print("❌ No training data in database")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False
    
    # Test HumeAI config
    print("\n2️⃣ Testing HumeAI Configuration...")
    try:
        url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"
        headers = {"X-Hume-Api-Key": HUME_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            config = response.json()
            prompt = config.get('prompt', {}).get('text', '')
            
            if 'CLARIFIES' in prompt and 'SalesAice' in prompt:
                print("✅ HumeAI config contains training data")
                print(f"   Prompt length: {len(prompt)} characters")
            else:
                print("⚠️ HumeAI config doesn't contain full training")
        else:
            print(f"❌ Failed to fetch HumeAI config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HumeAI test failed: {str(e)}")
        return False
    
    print("\n✅ All tests passed!")
    return True


def main():
    """Main training orchestration"""
    print("\n" + "=" * 100)
    print(" " * 30 + "🎓 SALESAICE AGENT TRAINING")
    print("=" * 100)
    print("\n📋 Training Methodology: CLARIFIES Framework")
    print("📦 Product: GTcree Eco-Friendly Smart Water Bottle")
    print("🎯 Goal: Train agent with world-class sales techniques")
    print("\n" + "=" * 100)
    
    # Step 1: Save to local database
    print("\n🔹 STEP 1: Save Training to Local Database")
    db_success = save_training_to_database()
    
    if not db_success:
        print("\n❌ Database save failed. Stopping training.")
        return
    
    # Step 2: Update HumeAI config
    print("\n🔹 STEP 2: Update HumeAI Configuration")
    user_input = input("\n⚠️  This will replace current HumeAI prompt. Continue? (y/n): ").lower()
    
    if user_input == 'y':
        hume_success = update_hume_config()
        
        if not hume_success:
            print("\n⚠️ HumeAI update failed, but local database has training data.")
    else:
        print("\n⏸️  Skipped HumeAI update. Local database still has training.")
        hume_success = False
    
    # Step 3: Test training
    print("\n🔹 STEP 3: Test Training Data Access")
    test_training()
    
    # Summary
    print("\n" + "=" * 100)
    print(" " * 35 + "📊 TRAINING SUMMARY")
    print("=" * 100)
    print(f"\n✅ Local Database: {'SUCCESS' if db_success else 'FAILED'}")
    print(f"{'✅' if hume_success else '⏸️ '} HumeAI Config: {'UPDATED' if hume_success else 'SKIPPED/FAILED'}")
    print("\n🎯 Next Steps:")
    print("   1. Restart Django server to load new training")
    print("   2. Make test call: python quick_call_test.py")
    print("   3. Agent will use CLARIFIES framework")
    print("   4. Listen for improved sales techniques")
    print("\n" + "=" * 100)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
