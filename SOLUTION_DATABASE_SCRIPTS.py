"""
🎯 COMPLETE GUIDE: Database Scripts Use Karne Ka Tarika

PROBLEM:
- HumeAI EVI runtime mein persona change NAHI karta
- Runtime "configure" message type support nahi karta
- Isliye database script directly inject nahi ho sakta

SOLUTION:
Har agent ka apna HumeAI config ID use karo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: HumeAI Dashboard Mein 3 Configs Banao
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. https://platform.hume.ai/ par jao
2. "Configs" section mein jao
3. 3 naye configs create karo:

   CONFIG A - Demo Agent:
   -------------------
   Name: Demo Agent Config
   System Prompt:
   ```
   You are a demo sales agent. Keep responses brief and professional.
   Maximum 2 sentences per response.
   ```
   
   CONFIG B - Test Agent (SalesAice):
   -------------------  
   Name: Test Agent - SalesAice
   System Prompt:
   ```
   You are calling from SalesAice.ai.
   
   Start with: "Hi, this is Test from SalesAice.ai. How are you today?"
   
   If customer responds positively, share this:
   "Hello! This is calling from SalesAice.ai — we help businesses grow faster 
   through smart AI-driven sales automation. Our platform automates repetitive 
   sales tasks, helps track leads effectively, and gives real-time performance 
   insights. I'd love to quickly show you how it works. Would you like me to 
   share a short demo or a quick overview?"
   
   RULES:
   - Maximum 2 sentences per response
   - No filler words
   - Be professional and concise
   ```
   
   CONFIG C - Live Test Agent:
   -------------------
   Name: Live Test Agent Config
   System Prompt:
   ```
   You are a live test agent for Pakistan calls.
   Keep responses brief and professional.
   Maximum 2 sentences per response.
   ```

4. Har config save karne ke baad CONFIG ID copy karo
   (Format: abcd1234-ef56-7890-ghij-klmnopqrstuv)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: Database Update Karo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this SQL (replace with your actual config IDs):

```sql
-- Demo Agent
UPDATE "HumeAiTwilio_humeagent" 
SET hume_config_id = 'YOUR_DEMO_CONFIG_ID'
WHERE name = 'Demo Sales Agent';

-- Test Agent  
UPDATE "HumeAiTwilio_humeagent"
SET hume_config_id = 'YOUR_TEST_CONFIG_ID' 
WHERE name = 'Test Agent';

-- Live Test Agent
UPDATE "HumeAiTwilio_humeagent"
SET hume_config_id = 'YOUR_LIVE_CONFIG_ID'
WHERE name = 'Live Test Agent - Pakistan Call';
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: Test Karo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Server restart NOT needed (config dynamically loaded from DB)

Test call:
```powershell
# Test Agent (index 2)
$body = @{phone_no='+923403471112'; agent_id='2'} | ConvertTo-Json
Invoke-RestMethod -Uri 'https://your-ngrok.ngrok-free.dev/api/hume-twilio/initiate-call/' -Method POST -Headers $headers -Body $body
```

Expected behavior:
✅ Agent: "Hi, this is Test from SalesAice.ai. How are you today?"
✅ Uses SalesAice script from HumeAI config
✅ No errors in logs
✅ Concise responses (max 2 sentences)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY THIS WORKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your code already does this:

Line ~462 in vonage_realtime_consumer.py:
```python
HUME_CONFIG_ID = self.call.agent.hume_config_id  # ✅ Gets from database
```

Line ~483:
```python
hume_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
```

✅ System already uses database config_id
✅ Just need to set different config IDs per agent
✅ Each config has its own system prompt (script)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALTERNATIVE (If you want automatic sync):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you want to automatically create HumeAI configs from database,
we need to use HumeAI Management API (different from EVI API):

1. POST to https://api.hume.ai/v0/evi/configs
2. Send system_prompt from database
3. Get config_id in response
4. Save config_id back to database

But this requires:
- HumeAI Management API key (different from EVI API key)
- Extra API calls on each agent creation
- More complex code

Current manual method is simpler and more reliable.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(__doc__)
