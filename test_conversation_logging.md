# ✅ Live Conversation Logging - ENABLED

## 📝 What's Saved to Database

Every time a call is answered and conversation happens, **ALL messages** are automatically saved to `ConversationLog` table:

### 1. **Customer Messages** (user_message event)
```python
ConversationLog.objects.create(
    call=call_object,
    role='user',
    message='Customer text here...',
    sentiment='',
    confidence=0.0,
    timestamp=now()
)
```

### 2. **AI Agent Messages** (assistant_message event)
```python
ConversationLog.objects.create(
    call=call_object,
    role='assistant',
    message='AI response text here...',
    sentiment='',
    confidence=0.0,
    timestamp=now()
)
```

### 3. **Emotion Data** (emotion event)
```python
ConversationLog.objects.create(
    call=call_object,
    role='system',  # or None
    emotion_scores={'joy': 0.8, 'sadness': 0.1, ...},
    sentiment='positive',
    confidence=0.85,
    timestamp=now()
)
```

## 🔄 How It Works

1. **Call Answered** → WebSocket connects to HumeAI
2. **Customer Speaks** → HumeAI sends `user_message` event
   - ✅ Logged to console
   - ✅ **SAVED to ConversationLog (role='user')**
3. **AI Responds** → HumeAI sends `assistant_message` event
   - ✅ Logged to console
   - ✅ **SAVED to ConversationLog (role='assistant')**
4. **Call Ends** → All conversation history in database

## 🎯 Database Structure

**Table: `conversation_logs`**
| Column | Type | Example |
|--------|------|---------|
| id | UUID | `a1b2c3d4-...` |
| call_id | ForeignKey | Link to TwilioCall |
| role | String | `'user'` or `'assistant'` |
| message | Text | `"Hello, how can I help?"` |
| emotion_scores | JSON | `{"joy": 0.8, ...}` |
| sentiment | String | `'positive'` |
| confidence | Float | `0.85` |
| timestamp | DateTime | `2025-11-02 12:30:45` |

## 📊 Query Examples

### Get all messages for a call:
```python
from HumeAiTwilio.models import TwilioCall, ConversationLog

call = TwilioCall.objects.get(call_sid='0487cb11-...')
messages = ConversationLog.objects.filter(call=call).order_by('timestamp')

for msg in messages:
    print(f"{msg.role}: {msg.message}")
```

### Get customer messages only:
```python
customer_messages = ConversationLog.objects.filter(
    call=call,
    role='user'
).order_by('timestamp')
```

### Get AI responses only:
```python
ai_responses = ConversationLog.objects.filter(
    call=call,
    role='assistant'
).order_by('timestamp')
```

## ✅ Verification Script

Run this to check if messages are being saved:

```bash
python scripts/check_db.py
```

## 🚀 Next Call Will Save Everything!

When you answer the next call:
- ✅ Every word customer says → Saved
- ✅ Every AI response → Saved
- ✅ All emotions detected → Saved
- ✅ Full conversation history → Available in database

**Test it now by making a call and checking the database!** 📞
