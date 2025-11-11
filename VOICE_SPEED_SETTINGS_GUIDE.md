# 🎯 HumeAI Voice Speed Settings - Complete Guide

## 📸 What You're Looking At

The screenshot you shared shows **"Temperature"** slider - that's **NOT for speed**!

### ❌ Temperature (What you showed me)
- **Purpose**: Controls AI **creativity/randomness**
- **Does NOT control**: Voice speed, tone, or prosody
- **Range**: Usually 0.0 to 1.0
- **Effect**: Higher = more creative/unpredictable responses

---

## ✅ What You Actually Need: Voice/TTS Settings

### 🔍 Where to Find Voice Speed Settings:

#### **Option 1: Voice Tab** (Most Common)
```
HumeAI Dashboard → Your Config → "Voice" Tab

Look for:
├── Voice Provider (dropdown)
├── Voice Selection (name/ID)
├── 📊 Speech Rate / Speed (SLIDER) ← THIS ONE!
├── Pitch (optional)
└── Volume (optional)
```

#### **Option 2: Built-In Voice (Hume's TTS)**
```
Configuration → Voice Settings → Built-in Voice

Settings:
- Voice Name: (select voice)
- Speed: [====|=====] ← Adjust this slider
  - Min: 0.5x (very slow)
  - Default: 1.0x (current - TOO SLOW)
  - Max: 2.0x (very fast)
  - Recommended: 1.3x to 1.5x
```

#### **Option 3: Custom Voice Provider** (Play.ht / ElevenLabs)
```
If using external TTS:
- Provider: Play.ht / ElevenLabs / Google / Azure
- Voice ID: (your selected voice)
- Speed/Rate: Slider or numeric input
```

---

## 📋 Step-by-Step Navigation

### 1️⃣ Login to HumeAI
```
URL: https://platform.hume.ai/
Login → Dashboard
```

### 2️⃣ Find Your Config
```
Left Sidebar → "EVI" or "Configurations"
Search for: 13624648-658a-49b1-81cb-a0f2e2b05de5
Click "Edit" or config name
```

### 3️⃣ Navigate Tabs
Look for these tabs (depends on HumeAI's UI version):
- ✅ **"Voice"** tab (most likely location)
- ✅ **"TTS Settings"** tab
- ✅ **"Speech Output"** tab
- ✅ **"Advanced Settings"** → Voice section
- ❌ NOT in "Model" or "Temperature" tabs

### 4️⃣ Find Speed Control
Look for any of these labels:
- **Speech Rate** 🎯 (most common)
- **Speed**
- **Rate**
- **Tempo**
- **Prosody Speed**

### 5️⃣ Adjust Slider
```
Current: [==========] 1.0x (100%)
Target:  [==============] 1.4x (140%) ← Move slider here
```

### 6️⃣ Save & Deploy
- Click **"Save"** or **"Update Configuration"**
- If there's a **"Deploy"** button, click it too
- Wait 5-10 seconds for changes to propagate

---

## 🎨 Visual Reference Guide

### What Settings Screen Should Look Like:

```
┌─────────────────────────────────────────────────┐
│  Configuration: Your EVI Config                 │
├─────────────────────────────────────────────────┤
│  Tabs: [Model] [Voice] [System Prompt] [...]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  📢 Voice Settings                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                                 │
│  Voice Provider:  [Hume AI ▼]                  │
│                                                 │
│  Voice Selection: [ITO ▼]                      │
│                                                 │
│  Speech Rate:                                   │
│  Slower ◄────────●────────► Faster             │
│           0.5x    1.4x    2.0x                  │
│  ⚠️ Move this slider → to 1.4x                 │
│                                                 │
│  Pitch: [────────●────────] (optional)         │
│                                                 │
│  [Cancel]              [Save Configuration]    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚨 Common Mistakes

### ❌ WRONG Settings (Don't Touch These):
1. **Temperature** ← Your screenshot (controls AI creativity)
2. **Top-P / Top-K** (model sampling)
3. **Max Tokens** (response length)
4. **Frequency Penalty** (word repetition)

### ✅ CORRECT Settings (What You Need):
1. **Speech Rate** / **Speed** (TTS/Voice section)
2. **Voice Provider** settings
3. **Prosody Controls** (if available)

---

## 🔧 Alternative: API Method

If you **CANNOT find the speed slider** in dashboard, use this API script:

```python
# update_voice_speed_api.py
import requests
import json

API_KEY = "YOUR_HUME_API_KEY"
CONFIG_ID = "13624648-658a-49b1-81cb-a0f2e2b05de5"

url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"

headers = {
    "X-Hume-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# First, get current config
response = requests.get(url, headers=headers)
current_config = response.json()
print("📋 Current Config:")
print(json.dumps(current_config, indent=2))

# Update voice settings
data = {
    "voice": {
        "provider": "HUME_AI",  # or your current provider
        "speed": 1.4,  # 40% faster than default
        # Add other voice settings as needed
    }
}

response = requests.patch(url, headers=headers, json=data)

if response.status_code == 200:
    print("\n✅ Voice speed updated to 1.4x!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.text)
```

**Run this script:**
```bash
venv\Scripts\activate
python update_voice_speed_api.py
```

---

## 📊 Recommended Speed Values

| Speed | Effect | Use Case |
|-------|--------|----------|
| 0.8x | 20% slower | Non-native speakers, elderly users |
| 1.0x | **Current (Default)** | ❌ Too slow/robotic |
| 1.2x | 20% faster | ✅ Natural conversation |
| 1.4x | 40% faster | ✅ **RECOMMENDED** - energetic, human-like |
| 1.6x | 60% faster | Fast talker, time-sensitive |
| 1.8x | 80% faster | ⚠️ May lose clarity |
| 2.0x | 2x speed | ❌ Too fast, hard to understand |

---

## 🎯 After Changing Speed

### Test Your Changes:
```bash
# 1. No need to restart Django (config fetched from HumeAI)
# 2. Just make a new test call
python quick_call_test.py

# 3. Answer call and listen
# AI should speak faster now!
```

---

## 💡 Pro Tips

1. **Start with 1.3x or 1.4x** - best balance of speed and clarity
2. **Test with actual phone call** - don't just test in browser
3. **Different voices have different "natural" speeds** - adjust per voice
4. **Twilio's audio compression** can affect perceived speed - test on real network
5. **If still too slow after 1.5x**, check if you're using the right voice provider

---

## 🆘 Still Can't Find It?

### Contact HumeAI Support:
```
📧 Email: support@hume.ai
💬 Discord: https://discord.gg/hume-ai
📖 Docs: https://dev.hume.ai/docs/evi/configuration

Ask them:
"Where can I adjust the speech rate/speed for my EVI config 
ID: 13624648-658a-49b1-81cb-a0f2e2b05de5? 
The AI speaks too slowly at default speed."
```

### Or Share Screenshot With Me:
1. Go to your config edit page
2. Take screenshot of **"Voice"** tab (not Temperature/Model tab)
3. Share it with me
4. I'll point exactly where the speed slider is!

---

## 📌 Quick Reference

**What You Need:**
- ✅ **Voice/TTS Settings** section
- ✅ **Speech Rate** or **Speed** slider
- ✅ Set to **1.4x** (40% faster)

**What You DON'T Need:**
- ❌ Temperature slider (your screenshot)
- ❌ Model settings
- ❌ System prompt changes

---

## ✅ Success Checklist

- [ ] Login to HumeAI Dashboard
- [ ] Navigate to Config: `13624648-658a-49b1-81cb-a0f2e2b05de5`
- [ ] Find **"Voice"** or **"TTS"** tab (NOT "Model" tab)
- [ ] Locate **Speech Rate/Speed** slider
- [ ] Move slider from **1.0x** to **1.4x**
- [ ] Click **Save** (and **Deploy** if available)
- [ ] Wait 10 seconds for changes to apply
- [ ] Make test call: `python quick_call_test.py`
- [ ] Listen - AI should speak faster now!

---

**🎯 Bottom Line:** Temperature slider (your screenshot) ≠ Voice speed. You need to find the **Voice/TTS settings section** with a **Speech Rate slider**!
