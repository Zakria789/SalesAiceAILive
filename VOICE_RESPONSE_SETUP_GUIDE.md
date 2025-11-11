# AI Agent Voice Response System - Setup Guide

## Agent ko Voice Main Response Dene ka Complete System

### 🎯 Overview
Yeh system aapke AI agents ko voice main responses dene ki capability deta hai. Customers ke messages ke liye intelligent voice responses generate karta hai.

### 🛠️ Installation & Setup

#### 1. Required Packages Install Karo
```bash
pip install pyttsx3
pip install SpeechRecognition
pip install pyaudio  # Optional, for microphone input
```

#### 2. System Files
- `agents/voice_response_system.py` - Main voice system
- `agents/voice_api_views.py` - API endpoints
- `agent_voice_demo.py` - Demo script

### 🎙️ Voice Response Features

#### 1. Automatic Voice Response Generation
```python
from agents.voice_response_system import get_agent_voice_response

# Simple usage
response = get_agent_voice_response(
    agent_id="your-agent-uuid",
    customer_message="Hello, I'm interested in your product"
)

print(response['text_response'])  # Text response
# Voice automatically plays through speakers
```

#### 2. Voice Settings Configuration
```python
from agents.voice_response_system import setup_agent_voice

# Configure agent voice
setup_agent_voice("agent-uuid", {
    "voice_tone": "professional",  # friendly, professional, enthusiastic, calm, confident
    "voice_model": "en-US-female-1",  # female/male voice selection
    "tone_settings": {
        "speaking_speed": "normal",
        "emotion_level": "moderate"
    }
})
```

#### 3. Emotion-Based Response
System automatically detects customer emotion aur appropriate response deta hai:
- **Interest**: Enthusiastic responses
- **Frustration**: Empathetic responses  
- **Curiosity**: Informative responses
- **Satisfaction**: Momentum building responses

### 🌐 API Endpoints

#### 1. Generate Voice Response
```http
POST /agents/voice/response/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "agent_id": "uuid-here",
    "customer_message": "Hello, I'm interested in your services",
    "context": {
        "product_interest": true,
        "customer_name": "John"
    }
}
```

**Response:**
```json
{
    "success": true,
    "response_data": {
        "text_response": "Hi John! This is Sarah, and I love your interest!",
        "voice_output": {"status": "completed"},
        "emotion_detected": {"primary_emotion": "interest"},
        "response_strategy": "engagement_focused"
    }
}
```

#### 2. Update Voice Settings
```http
POST /agents/voice/settings/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "agent_id": "uuid-here",
    "voice_settings": {
        "voice_tone": "professional",
        "voice_model": "en-US-female-1"
    }
}
```

#### 3. Test Voice Output
```http
POST /agents/voice/test/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "agent_id": "uuid-here",
    "test_message": "Hello! This is a voice test."
}
```

#### 4. Live Conversation
```http
POST /agents/{agent_id}/live-conversation/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "customer_message": "What are your pricing options?",
    "context": {
        "conversation_turn": 2,
        "customer_interest_level": "high"
    }
}
```

#### 5. Get Voice Settings
```http
GET /agents/{agent_id}/voice-settings/
Authorization: Bearer YOUR_TOKEN
```

### 🎚️ Voice Configuration Options

#### Voice Tones
- **friendly**: Warm, welcoming tone (160 WPM)
- **professional**: Business-like tone (140 WPM)  
- **enthusiastic**: Excited, energetic tone (180 WPM)
- **calm**: Soothing, relaxed tone (120 WPM)
- **confident**: Assertive, sure tone (150 WPM)

#### Voice Models
- **en-US-female-1**: Primary female voice
- **en-US-male-1**: Primary male voice
- **en-US-female-2**: Alternative female voice
- **en-US-male-2**: Alternative male voice

### 🤖 Agent Model Updates

Voice settings automatically save karte hain Agent model main:

```python
# Agent model main yeh fields available hain
agent.voice_model = "en-US-female-1"
agent.voice_tone = "professional" 
agent.tone_settings = {
    "speaking_speed": "normal",
    "emotion_level": "moderate"
}
```

### 🎬 Demo Script Usage

```bash
# Demo run karo
python agent_voice_demo.py

# Demo features:
# 1. Direct voice system test
# 2. API endpoints test  
# 3. Live conversation simulation
```

### 📱 Frontend Integration Examples

#### JavaScript/React Integration
```javascript
// Voice response generate karo
async function getAgentVoiceResponse(agentId, message) {
    const response = await fetch('/agents/voice/response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            agent_id: agentId,
            customer_message: message,
            context: {
                product_interest: true
            }
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        // Display text response
        displayAgentMessage(result.response_data.text_response);
        
        // Voice automatically plays on server side
        // You can also implement browser-based TTS here
        speakText(result.response_data.text_response);
    }
}

// Browser TTS function
function speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.8;
    utterance.pitch = 1;
    speechSynthesis.speak(utterance);
}
```

### 🔧 Advanced Configuration

#### Custom Emotion Detection
```python
# agents/voice_response_system.py main extend karo
class CustomAgentVoiceSystem(AgentVoiceResponseSystem):
    def detect_customer_emotion(self, message):
        # Your custom emotion detection logic
        # Hume AI integration
        # External API calls
        pass
```

#### Multi-language Support
```python
# Voice models for different languages
voice_models = {
    'en-US': ['en-US-female-1', 'en-US-male-1'],
    'es-ES': ['es-ES-female-1', 'es-ES-male-1'],
    'fr-FR': ['fr-FR-female-1', 'fr-FR-male-1']
}
```

### 🚀 Production Deployment

#### 1. Server Requirements
- Audio output capabilities
- pyttsx3 compatible TTS engine
- Sufficient CPU for voice processing

#### 2. Performance Optimization
```python
# Voice processing ko background thread main run karo
voice_thread = threading.Thread(target=speak_async)
voice_thread.start()
```

#### 3. Error Handling
```python
# Fallback responses for voice failures
if voice_output['status'] == 'failed':
    return text_only_response
```

### 🎯 Use Cases

#### 1. Sales Calls
- Enthusiastic voice for product presentations
- Empathetic voice for objection handling
- Professional voice for closing

#### 2. Customer Support
- Calm voice for problem resolution
- Friendly voice for general inquiries
- Confident voice for technical support

#### 3. Lead Generation
- Engaging voice for cold calls
- Persuasive voice for follow-ups
- Professional voice for B2B contacts

### 📊 Analytics & Monitoring

Voice response analytics track karo:
- Response generation time
- Voice output success rate
- Customer emotion detection accuracy
- Conversation effectiveness metrics

### 🔐 Security Considerations

- Voice data encryption
- Secure API endpoints
- User authentication required
- Rate limiting for voice requests

### 🆘 Troubleshooting

#### Common Issues:

1. **Voice not playing**
   - Check audio drivers
   - Verify pyttsx3 installation
   - Test system audio output

2. **API errors**
   - Verify authentication token
   - Check agent exists and is active
   - Validate request format

3. **Performance issues**
   - Use background threads for voice
   - Optimize emotion detection
   - Cache voice settings

### 📞 Support

For issues or feature requests:
- Check demo script output
- Review API response errors
- Test with simple voice output first

---

## Quick Start Checklist

✅ Install required packages  
✅ Import voice system files  
✅ Add voice API URLs  
✅ Run demo script  
✅ Test voice output  
✅ Configure agent voice settings  
✅ Integrate with frontend  

**System ready for voice responses! 🎉**