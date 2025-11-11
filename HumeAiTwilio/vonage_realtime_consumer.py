"""
[TARGET] Complete HumeAI EVI Integration for Vonage with Intelligent Response System
Real-time bidirectional audio streaming with real-time emotions + Web Search + Customer Learning
Works on Local Development & Production
Vonage WebSocket Stream → Django Consumer → HumeAI → Real-time emotions [OK]
Features:
- Auto web search if answer not in knowledge base
- Customer profile learning (name, email, company, preferences)
- Personalized greetings based on previous calls
"""

import json
import base64
import asyncio
import logging
import websockets
import audioop  # For audio format conversion
from typing import Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from pydub import AudioSegment
from pydub.effects import speedup
import io

logger = logging.getLogger(__name__)


class VonageRealTimeConsumer(AsyncWebsocketConsumer):
    """
    [TARGET] WebSocket consumer that bridges Vonage and HumeAI EVI
    Handles real-time bidirectional audio streaming for Vonage calls
    Works identically to Twilio consumer but uses Vonage WebSocket format
    
    NEW FEATURES:
    - Intelligent response with web search fallback
    - Customer profile learning and persistence
    - Personalized greetings on repeat calls
    """
    
    def _get_greeting_text(self) -> str:
        """
        🔥 NATURAL CONVERSATIONAL GREETING
        Returns a casual, friendly greeting without mentioning sales pitch
        Agent will introduce purpose ONLY when customer asks
        
        Returns:
            Natural greeting text (e.g., "Hello! How are you today?")
        """
        try:
            # Check for returning customer - personalized greeting
            if self.call and self.call.customer_profile and self.call.customer_profile.full_name:
                customer_name = self.call.customer_profile.full_name.split()[0]  # First name
                greeting = f"Hi {customer_name}! How are you doing today?"
                logger.info(f"👤 Using personalized natural greeting for returning customer")
                return greeting
            
            # Natural conversational greetings (NO sales pitch)
            logger.info(f"� Using natural conversational greeting (agent will introduce purpose when asked)")
            return "Hello! How are you today?"
            
        except Exception as e:
            logger.error(f"❌ Error getting greeting text: {e}")
            return "Hi! How can I help you today?"
    
    def _trim_wordy_response(self, text: str) -> str:
        """
        🔥 SAFETY NET: Trim wordy responses to max 2-3 sentences
        This is a fallback if HumeAI ignores the concise instructions
        
        Args:
            text: Original agent response
            
        Returns:
            Trimmed response (max 2-3 sentences or 250 chars)
        """
        try:
            # If already short, return as-is
            if len(text) <= 250:
                return text
            
            # Split into sentences (basic split by . ! ?)
            import re
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # If 3 or fewer sentences, return as-is
            if len(sentences) <= 3:
                return text
            
            # Take first 2 sentences and add period
            trimmed = '. '.join(sentences[:2]) + '.'
            
            # If still too long, hard cut at 250 chars
            if len(trimmed) > 250:
                trimmed = trimmed[:247] + '...'
            
            logger.info(f"✂️  [TRIM] Reduced from {len(sentences)} sentences to 2 sentences")
            return trimmed
            
        except Exception as e:
            logger.error(f"❌ Error trimming response: {e}")
            # If error, hard cut at 250 chars
            return text[:250] + '...' if len(text) > 250 else text
    
    def convert_linear16_to_linear16(self, linear_b64: str) -> str:
        """Vonage sends linear16 PCM, no conversion needed! (Unlike Twilio µ-law)"""
        try:
            if not linear_b64:
                logger.warning(f"[WARNING] Empty linear16 data provided")
                return ""
            
            # Decode base64 linear16 audio
            linear_data = base64.b64decode(linear_b64)
            
            if len(linear_data) == 0:
                logger.warning(f"[WARNING] Empty linear16 data after base64 decode")
                return ""
            
            # [BOOST] BOOST VONAGE VOLUME by 2.5x (150% louder for HumeAI detection)
            # Vonage audio is typically lower than Twilio, so boost more
            try:
                linear_data = audioop.mul(linear_data, 2, 2.5)
            except Exception as e:
                logger.warning(f"[WARNING] Volume boost failed: {e}")
            
            # Vonage uses 16kHz, HumeAI works best with 48kHz
            # Upsample: 16kHz → 48kHz (3x upsampling)
            try:
                linear_data = audioop.ratecv(linear_data, 2, 1, 16000, 48000, None)[0]
            except Exception as e:
                logger.warning(f"[WARNING] Resampling failed: {e}")
                # Continue with original if resampling fails
            
            # Encode back to base64
            linear_b64 = base64.b64encode(linear_data).decode('utf-8')
            
            # Log conversion success occasionally
            if not hasattr(self, '_conversion_count'):
                self._conversion_count = 0
            self._conversion_count += 1
            
            if self._conversion_count % 100 == 1:  # Log first and every 100th
                logger.info(f"[CONVERT] Vonage audio conversion #{self._conversion_count}: 16kHz linear16 → 48kHz (STUDIO QUALITY)")
            
            return linear_b64
            
        except Exception as e:
            logger.error(f"[ERROR] Vonage audio conversion error: {e}")
            return ""
    
    def convert_linear16_to_vonage_format(self, linear_b64: str) -> str:
        """Convert linear16 PCM from HumeAI back to Vonage format (16kHz linear16)"""
        try:
            # Decode base64 linear16 audio from HumeAI
            linear_data = base64.b64decode(linear_b64)
            
            # [BOOST] Downsample from 48kHz → 16kHz for Vonage
            # This ensures proper playback speed with studio-quality source
            try:
                linear_data = audioop.ratecv(linear_data, 2, 1, 48000, 16000, None)[0]
            except Exception as e:
                logger.warning(f"[WARNING] Vonage resampling failed: {e}")
            
            logger.info(f"[CONVERT] Converting audio: HumeAI linear16 48kHz → Vonage 16kHz")
            
            # Encode back to base64
            vonage_b64 = base64.b64encode(linear_data).decode('utf-8')
            
            logger.info(f"[OK] Vonage conversion successful")
            return vonage_b64
        except Exception as e:
            logger.error(f"[ERROR] Vonage audio conversion error: {e}")
            return linear_b64

    async def connect(self):
        """Accept WebSocket connection from Vonage"""
        try:
            await self.accept()
            
            # Initialize connection state
            self.call_uuid = None
            self.call = None
            self.hume_ws = None
            self.hume_connected = False
            self.intelligent_service = None  # 🔥 NEW: Intelligent response service
            
            logger.info("[CONNECT] Vonage WebSocket connection established")
            
            # Store in connection state for tracking
            self.hume_session = None
            
            # CRITICAL: Extract UUID from URL path
            # Vonage doesn't send "start" event - we get UUID from URL
            # In Channels, URL params are in self.scope['url_route']['kwargs']
            try:
                self.call_uuid = self.scope.get('url_route', {}).get('kwargs', {}).get('uuid')
                if self.call_uuid:
                    logger.info(f"[UUID] Extracted from URL: {self.call_uuid}")
                    # Initialize HumeAI immediately
                    await self.initialize_vonage_call()
                else:
                    logger.error("[ERROR] UUID not found in WebSocket URL")
                    logger.error(f"[DEBUG] scope keys: {self.scope.keys()}")
                    if 'url_route' in self.scope:
                        logger.error(f"[DEBUG] url_route: {self.scope['url_route']}")
            except Exception as e:
                logger.error(f"[ERROR] UUID extraction failed: {e}")
                logger.error(f"[DEBUG] Full scope: {self.scope}")
            
        except Exception as e:
            logger.error(f"[ERROR] Vonage WebSocket connection error: {str(e)}")
            await self.close()
    
    async def initialize_vonage_call(self):
        """Initialize call from database and connect to HumeAI"""
        try:
            logger.info(f"[INIT] Initializing Vonage call: {self.call_uuid}")
            
            # Find call in database
            from channels.db import database_sync_to_async
            from .models import TwilioCall
            from .intelligent_response_service import IntelligentResponseService
            
            @database_sync_to_async
            def get_call():
                return TwilioCall.objects.select_related('agent', 'customer_profile').filter(
                    call_sid=self.call_uuid,
                    provider='vonage'
                ).first()
            
            self.call = await get_call()
            
            if self.call:
                logger.info(f"[OK] Found Vonage call in database: {self.call.id}")
                
                # 🔥 NEW: Initialize Intelligent Response Service
                @database_sync_to_async
                def init_intelligent_service():
                    return IntelligentResponseService(call=self.call)
                
                self.intelligent_service = await init_intelligent_service()
                logger.info(f"🧠 [INTELLIGENCE] Intelligent service initialized")
                
                # Check if existing customer
                if self.call.customer_profile and self.call.customer_profile.full_name:
                    logger.info(f"👤 [RETURNING CUSTOMER] {self.call.customer_profile.full_name}")
                    logger.info(f"   Total previous calls: {self.call.customer_profile.total_calls}")
                else:
                    logger.info(f"✨ [NEW CUSTOMER] First time caller")
                
                # 🔥 NEW: Check for agent config (supports both HumeAgent and Agent models)
                agent_name = None
                agent_config_id = None
                
                if self.call.agent:
                    # Old way: Agent ForeignKey (HumeAgent model)
                    agent_name = self.call.agent.name
                    agent_config_id = getattr(self.call.agent, 'hume_config_id', None)
                    logger.info(f"   Agent (ForeignKey): {agent_name}")
                    if agent_config_id:
                        logger.info(f"   HumeAI Config (agent): {agent_config_id}")
                
                # Check call's hume_config_id field (set by call_initiation.py)
                if self.call.hume_config_id:
                    agent_config_id = self.call.hume_config_id
                    logger.info(f"   HumeAI Config (call field): {agent_config_id}")
                
                # Check customer_name field for agent name (temporary storage)
                if not agent_name and self.call.customer_name and 'Agent:' in str(self.call.customer_name):
                    # Extract agent name from customer_name if stored there
                    agent_name = self.call.customer_name
                    logger.info(f"   Agent (customer_name): {agent_name}")
                elif not agent_name:
                    agent_name = 'None'
                    logger.info(f"   Agent: {agent_name}")
                
                # Store for use in initialize_hume_session
                self.agent_config_id = agent_config_id
                
                if self.call.agent or agent_config_id:
                    # Create HumeAI WebSocket session
                    await self.initialize_hume_session()
                else:
                    logger.warning(f"[WARNING] No agent assigned to call: {self.call_uuid}")
            else:
                logger.warning(f"[WARNING] Vonage call not found in database: {self.call_uuid}")
                logger.warning(f"   UUID: {self.call_uuid}")
                logger.warning(f"   Provider: vonage")
        
        except Exception as e:
            logger.error(f"[ERROR] Initialize Vonage call error: {str(e)}", exc_info=True)

    async def disconnect(self, close_code):
        """Handle Vonage WebSocket disconnection - Final cleanup"""
        try:
            logger.info(f"🔌 [DISCONNECT] Vonage WebSocket disconnected")
            logger.info(f"   Close code: {close_code}")
            logger.info(f"   Call UUID: {self.call_uuid}")
            
            # ✅ STEP 1: Close HumeAI connection if still open
            if self.hume_ws and not self.hume_ws.closed:
                await self.hume_ws.close()
                logger.info(f"✅ [HUME] HumeAI WebSocket closed in disconnect")
                self.hume_connected = False
            else:
                logger.info(f"ℹ️  [HUME] HumeAI already closed")
            
            # ✅ STEP 2: Update call status in database (if not already done)
            if self.call:
                from channels.db import database_sync_to_async
                
                @database_sync_to_async
                def update_call():
                    # Only update if not already completed
                    if self.call.status != 'completed':
                        self.call.status = 'completed'
                        self.call.ended_at = timezone.now()
                        if self.call.started_at:
                            self.call.duration = int(
                                (self.call.ended_at - self.call.started_at).total_seconds()
                            )
                        self.call.save()
                        
                        # 🔄 REACTIVATE AGENT: Call khatam hone par agent ko active kar do
                        # Only works with HumeAgent ForeignKey (not Agent model from agents app)
                        if self.call.agent and hasattr(self.call.agent, 'status'):
                            self.call.agent.status = 'active'
                            self.call.agent.save(update_fields=['status'])
                            logger.info(f"🔄 [AGENT] Agent '{self.call.agent.name}' reactivated in disconnect")
                        
                        return True
                    return False
                
                updated = await update_call()
                if updated:
                    logger.info(f"✅ [DB] Call {self.call_uuid} marked as 'completed'")
                else:
                    logger.info(f"ℹ️  [DB] Call {self.call_uuid} already marked as completed")
            
            logger.info(f"✅ [CLEANUP] All connections closed for call {self.call_uuid}")
        
        except Exception as e:
            logger.error(f"❌ [ERROR] Disconnect error: {str(e)}", exc_info=True)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive data from Vonage WebSocket
        Vonage sends audio and events in binary and text format
        """
        try:
            if text_data:
                data = json.loads(text_data)
                event = data.get('event')
                
                if event == 'start':
                    await self.handle_start(data)
                elif event == 'media':
                    await self.handle_media(data)
                elif event == 'stop':
                    await self.handle_stop(data)
            
            # Handle binary audio data from Vonage
            if bytes_data:
                await self.handle_binary_audio(bytes_data)
        
        except json.JSONDecodeError:
            logger.debug("Binary audio data received (not JSON)")
        except Exception as e:
            logger.error(f"[ERROR] Vonage receive error: {str(e)}", exc_info=True)

    async def handle_start(self, data):
        """Handle stream start event from Vonage"""
        try:
            start_data = data.get('start', {})
            self.call_uuid = start_data.get('uuid') or start_data.get('callUuid')
            
            logger.info(f"[CALL] Vonage stream started: UUID={self.call_uuid}")
            
            if self.call_uuid:
                # Find call in database
                from channels.db import database_sync_to_async
                from .models import TwilioCall
                
                @database_sync_to_async
                def get_call():
                    return TwilioCall.objects.filter(
                        call_sid=self.call_uuid,
                        provider='vonage'
                    ).first()
                
                self.call = await get_call()
                
                if self.call:
                    logger.info(f"[OK] Found Vonage call in database: {self.call.id}")
                    
                    # 🔄 SET AGENT STATUS TO BUSY when call starts
                    # Only works with HumeAgent ForeignKey (not Agent model from agents app yet)
                    if self.call.agent and hasattr(self.call.agent, 'status'):
                        @database_sync_to_async
                        def set_agent_busy():
                            if self.call.agent.status != 'busy':
                                self.call.agent.status = 'busy'
                                self.call.agent.save(update_fields=['status'])
                                agent_name = self.call.agent.name
                                config_id = getattr(self.call.agent, 'hume_config_id', 'N/A')
                                logger.info(f"🔄 [AGENT] Agent '{agent_name}' (Config: {config_id}) set to BUSY")
                        
                        await set_agent_busy()
                        
                        # Create HumeAI WebSocket session
                        await self.initialize_hume_session()
                    elif self.call.hume_config_id:
                        # Agent info stored in call's hume_config_id field
                        logger.info(f"[OK] Using hume_config_id from call: {self.call.hume_config_id}")
                        await self.initialize_hume_session()
                    else:
                        logger.warning(f"[WARNING]  No agent assigned to call: {self.call_uuid}")
                else:
                    logger.warning(f"[WARNING]  Vonage call not found in database: {self.call_uuid}")
        
        except Exception as e:
            logger.error(f"[ERROR] Handle start error: {str(e)}", exc_info=True)

    async def initialize_hume_session(self):
        """Initialize HumeAI WebSocket session for Vonage call"""
        try:
            # Import HumeAI config
            from decouple import config
            
            HUME_API_KEY = config('HUME_API_KEY', default='')
            
            # 🔥 USE AGENT'S CONFIG ID FROM DATABASE (not env variable)
            # This allows different agents to use different configurations
            
            # Check multiple sources for config_id (in priority order):
            # 1. self.agent_config_id (set in initialize_vonage_call from call.hume_config_id)
            # 2. agent.hume_config_id (for HumeAgent model - legacy)
            # 3. call.hume_config_id (direct field on call)
            # 4. Environment variable (fallback)
            
            HUME_CONFIG_ID = None
            
            if hasattr(self, 'agent_config_id') and self.agent_config_id:
                HUME_CONFIG_ID = self.agent_config_id
                logger.info(f"[OK] Using config from call: {HUME_CONFIG_ID}")
            elif self.call and self.call.agent and hasattr(self.call.agent, 'hume_config_id'):
                HUME_CONFIG_ID = self.call.agent.hume_config_id
                logger.info(f"[OK] Using agent's config: {HUME_CONFIG_ID}")
            elif self.call and self.call.hume_config_id:
                HUME_CONFIG_ID = self.call.hume_config_id
                logger.info(f"[OK] Using call's hume_config_id field: {HUME_CONFIG_ID}")
            
            # Fallback to env variable if agent config not set
            if not HUME_CONFIG_ID:
                HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')
                logger.warning(f"⚠️  No config found, using default from env: {HUME_CONFIG_ID[:8]}...")
            
            if not HUME_API_KEY or not HUME_CONFIG_ID:
                logger.error("[ERROR] HumeAI credentials not configured")
                return
            
            # [CONFIG] CORRECT HumeAI EVI endpoint with config_id parameter
            # Uses X-Hume-Api-Key header, NOT Bearer token!
            hume_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
            
            try:
                logger.info(f"🔌 [HUME] Connecting to HumeAI EVI...")
                logger.info(f"   URL: {hume_url[:50]}...")
                logger.info(f"   Config ID: {HUME_CONFIG_ID}")
                logger.info(f"   Call UUID: {self.call_uuid}")
                
                # Connect to HumeAI with correct headers
                self.hume_ws = await asyncio.wait_for(
                    websockets.connect(
                        hume_url,
                        extra_headers={"X-Hume-Api-Key": HUME_API_KEY},
                        ping_interval=20,
                        ping_timeout=20
                    ),
                    timeout=10.0
                )
                
                self.hume_connected = True
                logger.info(f"✅ [HUME] CONNECTED to HumeAI EVI successfully!")
                logger.info(f"   Call: {self.call_uuid}")
                logger.info(f"   Agent: {self.call.agent.name if self.call and self.call.agent else 'N/A'}")
                
                # Send session configuration to HumeAI
                # 🎯 OPTIMIZED CONFIG: Audio + Turn-taking for better listening
                # ✅ FIXED: Agent waits for customer to finish speaking
                # ✅ FIXED: Faster response with optimized thresholds
                session_config = {
                    "type": "session_settings",
                    "config_id": HUME_CONFIG_ID,
                    "audio": {
                        "encoding": "linear16",
                        "channels": 1,
                        "sample_rate": 48000
                    },
                 "voice": {
                        "rate": 1.1,     # ⚡ Slightly faster = quicker responses (was 0.95)
                        "pitch": 1.0,
                        "energy": 1.0,   # ⚡ More energy = confident & fast (was 0.9)
                        "volume": 1.2,
                        "style": "professional"
                        },
                # ⚡ FAST RESPONSE: Optimized for quick agent replies
                "turn_taking": {
                    "mode": "natural",                 # 👥 Natural human turn-taking
                    "silence_threshold_ms": 600,       # ⚡ Reduced from 800ms (faster detection)
                    "interruption_threshold_ms": 300,  # ⚡ Reduced from 400ms (quicker interruptions)
                    "word_threshold": 3,               # ⚡ Reduced from 4 (respond sooner)
                    "interruption_enabled": True,      # ✅ Natural interruptions allowed
                    "vad_sensitivity": "high",         # ⚡ High sensitivity = faster detection
                    "end_of_turn_threshold_ms": 500,   # ⚡ Reduced from 600ms (quicker responses)
                    "backoff_ms": 150,                 # ⚡ Reduced from 200ms (less hesitation)
                    "wait_for_customer": True,         # ✅ Patient listening
                    "auto_continue": False,            # ❌ Don't rush - let customer think
                    "allow_overlap": True,
                    "pause_after_greeting_ms": 2000    # ⚡ Reduced from 2000ms (faster greeting)
                },
                # 🔊🔊 LOUD & CLEAR: Customer voice crystal clear
                "audio_input": {
                    "gain": 2.0,                       # 🔥 Reduced from 3.5 to prevent clipping
                    "noise_suppression": True,         # Remove background noise
                    "echo_cancellation": True,         # Remove echo
                    "auto_gain_control": True,         # Auto-adjust volume
                    "voice_boost": True,
                    "pause_after_greeting_ms": 2000    # Extra clarity boost
                },
                # 👥 FRIENDLY GREETING: Use from database or default
                "greeting": {
                    "enabled": True,
                    "text": self._get_greeting_text()  # 🔥 Get from DB sales_script or default
                },
                # 😌 PATIENT SILENCE HANDLING: Give customer time to think!
                "silence_handling": {
                    "enabled": True,
                    "max_wait_ms": 5000,               # Wait 5 seconds (patient!)
                    "prompt_after_silence": "You there?",  # Casual check-in
                    "auto_continue": False,            # ❌ Don't rush them
                    "patience_level": "high"           # 🧘 Very patient
                }
                }
                
                await self.hume_ws.send(json.dumps(session_config))
                logger.info(f"✅ [HUME] Minimal audio config sent")
                logger.info(f"   🔊 Audio: 48kHz linear16 mono")
                logger.info(f"   🎯 Cloud Config ID: {HUME_CONFIG_ID}")
                logger.info(f"   📝 Persona from cloud (runtime override NOT supported)")
                
                # 🔥 FORCE GREETING: Send greeting as assistant_input to trigger speech
                # HumeAI EVI needs explicit trigger to start speaking
                greeting_text = self._get_greeting_text()
                greeting_message = {
                    "type": "assistant_input",
                    "text": greeting_text
                }
                
                await self.hume_ws.send(json.dumps(greeting_message))
                logger.info(f"🎤 [GREETING] Sent greeting as assistant_input: '{greeting_text}'")
                logger.info(f"   ✅ Agent will speak first now!")
                
                # Start listening for HumeAI responses
                asyncio.create_task(self.listen_hume_responses())
                logger.info(f"👂 [HUME] Listening for AI responses...")
                
            except asyncio.TimeoutError:
                logger.error(f"[ERROR] HumeAI connection timeout (10s)")
                self.hume_connected = False
            except Exception as e:
                logger.error(f"[ERROR] Failed to connect to HumeAI: {e}")
                self.hume_connected = False
        
        except Exception as e:
            logger.error(f"[ERROR] Initialize HumeAI session error: {str(e)}", exc_info=True)

    async def handle_media(self, data):
        """Handle audio media event from Vonage"""
        try:
            media = data.get('media', {})
            payload = media.get('payload')  # Base64 encoded linear16 audio
            
            if payload and self.hume_connected and self.call:
                logger.debug(f"[AUDIO] Received audio chunk for call: {self.call_uuid}")
                
                # Convert audio format
                converted_audio = self.convert_linear16_to_linear16(payload)
                
                # ✅ FIXED: Removed empty text message - audio-only mode for faster processing
                # Audio is sent separately via handle_binary_audio()
        
        except Exception as e:
            logger.error(f"[ERROR] Handle media error: {str(e)}", exc_info=True)

    async def handle_binary_audio(self, bytes_data):
        """Handle raw binary audio data from Vonage"""
        try:
            if self.hume_connected and self.call:
                # Log every 50th audio packet to avoid spam
                if not hasattr(self, '_audio_count'):
                    self._audio_count = 0
                self._audio_count += 1
                
                if self._audio_count == 1:
                    logger.info(f"🎤 [CUSTOMER] Started receiving audio from customer")
                    logger.info(f"   Call: {self.call_uuid}")
                    logger.info(f"   Audio format: {len(bytes_data)} bytes linear16")
                
                if self._audio_count % 50 == 0:
                    logger.info(f"🎤 [CUSTOMER] Audio packet #{self._audio_count} ({len(bytes_data)} bytes)")
                
                # Convert audio format if needed
                # Vonage sends linear16, HumeAI expects linear16 (but at different sample rate)
                
                # 🔥 BOOST VOLUME 2x (200%) - Balanced for clear audio without clipping
                try:
                    audio_data = audioop.mul(bytes_data, 2, 2.0)  # 2x boost (reduced from 4x)
                    logger.debug(f"🔊 Volume boosted 2x (original: {len(bytes_data)} bytes)")
                except:
                    audio_data = bytes_data
                    logger.warning(f"⚠️ Volume boost failed, using original audio")
                
                # Resample: 16kHz → 48kHz
                try:
                    audio_data = audioop.ratecv(audio_data, 2, 1, 16000, 48000, None)[0]
                except:
                    pass
                
                # Send to HumeAI
                if self.hume_ws:
                    try:
                        await self.hume_ws.send(audio_data)
                        if self._audio_count == 1:
                            logger.info(f"📤 [HUME] First audio packet sent to HumeAI (48kHz)")
                    except Exception as e:
                        logger.error(f"❌ [ERROR] Error sending audio to HumeAI: {e}")
        
        except Exception as e:
            logger.error(f"❌ [ERROR] Binary audio error: {str(e)}", exc_info=True)

    async def listen_hume_responses(self):
        """Listen for HumeAI responses and emotions"""
        try:
            if not self.hume_ws:
                logger.warning("⚠️  [HUME] WebSocket not connected")
                return
            
            logger.info(f"👂 [HUME] Started listening for AI responses...")
            response_count = 0
            
            async for message in self.hume_ws:
                try:
                    response = json.loads(message)
                    event_type = response.get('type')
                    
                    response_count += 1
                    
                    # 🔍 DEBUG: Log ALL event types to understand HumeAI behavior
                    if response_count <= 10 or event_type in ['user_message', 'assistant_message', 'error']:
                        logger.info(f"🔍 [DEBUG #{response_count}] Event type: {event_type}")
                        logger.info(f"   Full response keys: {list(response.keys())}")
                        
                        # 🔥 LOG ERRORS IMMEDIATELY
                        if event_type == 'error':
                            error_code = response.get('code', 'unknown')
                            error_slug = response.get('slug', 'unknown')
                            error_message = response.get('message', 'No message')
                            logger.error(f"❌ [HUME ERROR] Code: {error_code}, Slug: {error_slug}")
                            logger.error(f"   Message: {error_message}")
                            logger.error(f"   Full error: {response}")
                    
                    # Log different event types
                    if event_type == 'emotion':
                        emotions = response.get('emotions', {})
                        logger.info(f"😊 [HUME] Emotion detected: {emotions}")
                        await self.capture_emotions(response)
                    
                    elif event_type == 'audio_output':
                        logger.info(f"🎵 [AGENT] AI sending audio response #{response_count}")
                        await self.send_audio_to_vonage(response)
                    
                    elif event_type == 'user_message':
                        # 🎯 HUMAN-LIKE: Extract customer speech
                        msg = response.get('message', {})
                        text = msg.get('content', msg.get('text', '')) if isinstance(msg, dict) else str(msg)
                        
                        # Try alternate paths for transcript
                        if not text and isinstance(response, dict):
                            text = response.get('text', response.get('content', ''))
                        
                        if text and text.strip():
                            logger.info(f"💬 [CUSTOMER] \"{text[:100]}...\"" if len(text) > 100 else f"💬 [CUSTOMER] \"{text}\"")
                            await self.save_conversation_message('user', text.strip())
                        else:
                            logger.debug(f"⚠️  [CUSTOMER] Empty transcript received")
                    
                    elif event_type == 'assistant_message':
                        # 🤖 HUMAN-LIKE: Extract agent response
                        msg = response.get('message', {})
                        text = msg.get('content', msg.get('text', '')) if isinstance(msg, dict) else str(msg)
                        
                        # Try alternate paths for response text
                        if not text and isinstance(response, dict):
                            text = response.get('text', response.get('content', ''))
                        
                        if text and text.strip():
                            # 🔥 SAFETY NET: Trim response if too wordy (fallback if HumeAI ignores concise rule)
                            original_text = text.strip()
                            trimmed_text = self._trim_wordy_response(original_text)
                            
                            if len(trimmed_text) < len(original_text):
                                logger.warning(f"⚠️  [TRIM] Agent response was wordy ({len(original_text)} chars), trimmed to {len(trimmed_text)} chars")
                                text = trimmed_text
                            
                            logger.info(f"🤖 [AGENT] \"{text[:100]}...\"" if len(text) > 100 else f"🤖 [AGENT] \"{text}\"")
                            await self.save_conversation_message('assistant', text)
                        else:
                            logger.debug(f"⚠️  [AGENT] Empty response received")
                    
                    else:
                        logger.debug(f"📨 [HUME] Event: {event_type}")
                
                except json.JSONDecodeError:
                    # Binary audio response
                    if message:
                        logger.info(f"🎵 [AGENT] Binary audio response ({len(message)} bytes)")
                        await self.send_raw_audio_to_vonage(message)
                
                except Exception as e:
                    logger.error(f"❌ [ERROR] Error processing HumeAI response: {e}")
        
        except Exception as e:
            logger.error(f"❌ [ERROR] Listen HumeAI error: {str(e)}")

    async def capture_emotions(self, response):
        """Capture emotion data from HumeAI and save to database"""
        try:
            if not self.call:
                return
            
            emotions = response.get('emotions', {})
            
            from channels.db import database_sync_to_async
            from .models import ConversationLog
            from .services.analytics_processor import AnalyticsProcessor
            
            @database_sync_to_async
            def save_emotion_log():
                return ConversationLog.objects.create(
                    call=self.call,
                    emotion_scores=emotions,
                    sentiment=response.get('sentiment', 'neutral'),
                    confidence=response.get('confidence', 0.0),
                    raw_response=response
                )
            
            log = await save_emotion_log()
            logger.info(f"[OK] Emotions saved for Vonage call {self.call_uuid}: {emotions}")
            
            # 📊 Update analytics in real-time with Hume AI emotion scores
            @database_sync_to_async
            def update_analytics():
                try:
                    AnalyticsProcessor.update_analytics_on_new_message(
                        call_sid=str(self.call.call_sid),
                        message="emotion_update",
                        role="system",
                        emotion_scores=emotions
                    )
                    logger.info(f"📊 Real-time analytics updated for call {self.call_uuid}")
                except Exception as e:
                    logger.error(f"Analytics update failed: {e}")
            
            await update_analytics()
        
        except Exception as e:
            logger.error(f"[ERROR] Capture emotions error: {str(e)}", exc_info=True)

    async def save_conversation_message(self, role: str, text: str, sentiment: str = '', confidence: float = 0.0, metadata: dict = None):
        """💾 Save conversation message (user/assistant) to ConversationLog database + Learn customer info"""
        try:
            if not self.call or not text:
                return None
            
            from channels.db import database_sync_to_async
            from .models import ConversationLog
            from .services.analytics_processor import AnalyticsProcessor
            
            @database_sync_to_async
            def _save_message():
                return ConversationLog.objects.create(
                    call=self.call,
                    role=role,
                    message=text,
                    sentiment=sentiment or '',
                    confidence=confidence,
                    metadata=metadata or {}
                )
            
            log = await _save_message()
            logger.info(f"💾 [DB] Saved {role} message to ConversationLog (call: {self.call_uuid})")
            
            # 📊 Update analytics in real-time when message includes emotions
            if log and hasattr(log, 'emotion_scores') and log.emotion_scores:
                @database_sync_to_async
                def update_analytics():
                    try:
                        AnalyticsProcessor.update_analytics_on_new_message(
                            call_sid=str(self.call.call_sid),
                            message=text,
                            role=role,
                            emotion_scores=log.emotion_scores
                        )
                        logger.info(f"📊 Analytics updated for message in call {self.call_uuid}")
                    except Exception as e:
                        logger.error(f"Analytics update failed: {e}")
                
                await update_analytics()
            
            # 🔥 NEW: Learn customer information from messages
            if self.intelligent_service and role == 'user':
                @database_sync_to_async
                def learn_customer_info():
                    self.intelligent_service.update_customer_info(text, role)
                
                await learn_customer_info()
            
            return log
        
        except Exception as e:
            logger.error(f"❌ [ERROR] Save conversation message error: {e}", exc_info=True)
            return None

    async def send_audio_to_vonage(self, response):
        """Send audio response from HumeAI back to Vonage"""
        try:
            # HumeAI sends 'data' not 'audio'!
            audio_payload = response.get('data') or response.get('audio')
            
            if audio_payload:
                # audio_payload is base64 encoded from HumeAI
                # Decode it to get raw bytes
                audio_bytes = base64.b64decode(audio_payload)
                
                # Convert from HumeAI format (48kHz linear16) to Vonage format (16kHz linear16)
                try:
                    # Downsample: 48kHz → 16kHz
                    audio_bytes = audioop.ratecv(audio_bytes, 2, 1, 48000, 16000, None)[0]
                except Exception as e:
                    logger.warning(f"⚠️  Audio resampling failed: {e}")
                
                # Send RAW BINARY audio to Vonage (not JSON!)
                await self.send(bytes_data=audio_bytes)
                logger.info(f"📞 [AGENT] Audio sent to customer ({len(audio_bytes)} bytes binary)")
            else:
                logger.warning(f"⚠️  No audio data in response: {list(response.keys())}")
        
        except Exception as e:
            logger.error(f"❌ [ERROR] Send audio to Vonage error: {str(e)}", exc_info=True)

    async def send_raw_audio_to_vonage(self, audio_bytes):
        """Send raw binary audio response to Vonage"""
        try:
            if audio_bytes:
                # Encode to base64 for JSON transport
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                message = {
                    'event': 'media',
                    'media': {
                        'payload': audio_b64
                    }
                }
                
                await self.send(text_data=json.dumps(message))
                logger.debug(f"[SEND] Sent binary audio response to Vonage ({len(audio_bytes)} bytes)")
        
        except Exception as e:
            logger.error(f"[ERROR] Send raw audio error: {str(e)}", exc_info=True)

    async def handle_stop(self, data):
        """Handle stream stop event from Vonage - Call completed"""
        try:
            logger.info(f"🛑 [STOP] Vonage stream stopped for call: {self.call_uuid}")
            logger.info(f"   Reason: Call completed/disconnected")
            
            # ✅ STEP 1: Close HumeAI connection immediately
            if self.hume_ws and not self.hume_ws.closed:
                await self.hume_ws.close()
                logger.info(f"✅ [HUME] HumeAI WebSocket closed successfully")
                self.hume_connected = False
            else:
                logger.info(f"ℹ️  [HUME] HumeAI already closed or not connected")
            
            # ✅ STEP 2: Update call status in database + Reactivate agent
            if self.call:
                from channels.db import database_sync_to_async
                
                @database_sync_to_async
                def update_call_status():
                    # Update call record
                    self.call.status = 'completed'
                    self.call.ended_at = timezone.now()
                    if self.call.started_at:
                        self.call.duration = int(
                            (self.call.ended_at - self.call.started_at).total_seconds()
                        )
                    self.call.save()
                    
                    # 🔄 REACTIVATE AGENT: Call khatam hone par agent ko active kar do
                    if self.call.agent:
                        self.call.agent.status = 'active'
                        self.call.agent.save(update_fields=['status'])
                        logger.info(f"🔄 [AGENT] Agent '{self.call.agent.name}' (ID: {self.call.agent.hume_config_id}) reactivated after call completion")
                    
                    return self.call.duration
                
                duration = await update_call_status()
                logger.info(f"✅ [DB] Call {self.call_uuid} marked as 'completed'")
                logger.info(f"   Duration: {duration} seconds")
            
            # ✅ STEP 3: Close Vonage WebSocket connection
            await self.close()
            logger.info(f"✅ [VONAGE] WebSocket connection closed")
        
        except Exception as e:
            logger.error(f"❌ [ERROR] Handle stop error: {str(e)}", exc_info=True)
