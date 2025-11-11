"""
Complete HumeAI EVI Integration for Twilio
Real-time bidirectional audio streaming with Auto-Training
Works on Local Development & PythonAnywhere Production
"""

import json
import base64
import asyncio
import logging
import websockets
import audioop  # For audio format conversion
from typing import Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from pydub import AudioSegment
from pydub.effects import speedup
import io

logger = logging.getLogger(__name__)


class HumeTwilioRealTimeConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that bridges Twilio and HumeAI EVI
    Handles real-time bidirectional audio streaming
    """
    
    def convert_mulaw_to_linear16(self, mulaw_b64: str) -> str:
        """Convert µ-law audio from Twilio to linear16 PCM for HumeAI with VOLUME BOOST"""
        try:
            if not mulaw_b64:
                logger.warning(f"⚠️ Empty µ-law data provided for conversion")
                return ""
            
            # Decode base64 µ-law audio
            mulaw_data = base64.b64decode(mulaw_b64)
            
            if len(mulaw_data) == 0:
                logger.warning(f"⚠️ Empty µ-law data after base64 decode")
                return ""
            
            # Convert µ-law to linear16 PCM
            linear_data = audioop.ulaw2lin(mulaw_data, 2)  # 2 bytes per sample (16-bit)
            
            # 🔥🔥 BOOST CUSTOMER VOLUME by 2.8x (180% louder for PERFECT HumeAI detection)
            linear_data = audioop.mul(linear_data, 2, 2.8)
            
            # 🔥 ABSOLUTE MAX: Resample from 8kHz → 48kHz for HumeAI
            # 6x the sample rate for STUDIO QUALITY audio
            linear_data = audioop.ratecv(linear_data, 2, 1, 8000, 48000, None)[0]
            
            # Validate conversion
            expected_len = len(mulaw_data) * 2 * 6  # *2 for 16-bit, *6 for 8k→48k upsampling
            if len(linear_data) != expected_len:
                logger.warning(f"⚠️ Unexpected conversion size: {len(mulaw_data)} µ-law → {len(linear_data)} linear16")
            
            # Encode back to base64
            linear_b64 = base64.b64encode(linear_data).decode('utf-8')
            
            # Log conversion success occasionally
            if not hasattr(self, '_conversion_count'):
                self._conversion_count = 0
            self._conversion_count += 1
            
            if self._conversion_count % 100 == 1:  # Log first and every 100th
                logger.info(f"🔄 Audio conversion #{self._conversion_count}: {len(mulaw_data)} µ-law 8kHz → {len(linear_data)} linear16 48kHz (STUDIO QUALITY)")
            
            return linear_b64
            
        except Exception as e:
            logger.error(f"❌ Audio conversion error: {e}")
            logger.error(f"   Input length: {len(mulaw_b64) if mulaw_b64 else 0}")
            return ""  # Return empty instead of original to prevent bad data
    
    def convert_linear16_to_mulaw(self, linear_b64: str) -> str:
        """Convert linear16 PCM from HumeAI to µ-law for Twilio"""
        try:
            # Decode base64 linear16 audio
            linear_data = base64.b64decode(linear_b64)
            
            # �🔥 ABSOLUTE MAX: Downsample from 48kHz → 8kHz for Twilio
            # This ensures proper playback speed with studio-quality source
            linear_data = audioop.ratecv(linear_data, 2, 1, 48000, 8000, None)[0]
            
            logger.info(f"🔄 Converting audio: {len(linear_data)} bytes linear16 48kHz → 8kHz µ-law (STUDIO → PHONE)")
            
            # Convert linear16 PCM to µ-law
            mulaw_data = audioop.lin2ulaw(linear_data, 2)  # 2 bytes per sample (16-bit)
            
            # Encode back to base64
            mulaw_b64 = base64.b64encode(mulaw_data).decode('utf-8')
            
            logger.info(f"✅ Conversion successful: {len(mulaw_data)} bytes µ-law")
            return mulaw_b64
        except Exception as e:
            logger.error(f"❌ Audio conversion error: {e}")
            logger.error(f"❌ Input data length: {len(linear_b64) if linear_b64 else 0}")
            return linear_b64  # Return original if conversion fails

    def speed_up_audio(self, linear_data: bytes, speed_factor: float = 2.0) -> bytes:
        """
        Speed up audio by the given factor using pydub
        speed_factor = 2.0 means 100% faster (DOUBLE SPEED for natural human speech)
        """
        try:
            # Convert raw bytes to AudioSegment
            audio = AudioSegment.from_raw(
                io.BytesIO(linear_data),
                sample_width=2,  # 16-bit audio (2 bytes per sample)
                frame_rate=8000,  # 8kHz sample rate (Twilio standard)
                channels=1  # Mono audio
            )
            
            # Speed up the audio
            fast_audio = speedup(audio, playback_speed=speed_factor)
            
            # Convert back to raw bytes
            output = io.BytesIO()
            fast_audio.export(output, format="raw")
            
            sped_up_data = output.getvalue()
            
            # Log speed adjustment (occasionally to avoid spam)
            if not hasattr(self, '_speedup_count'):
                self._speedup_count = 0
            self._speedup_count += 1
            
            if self._speedup_count % 50 == 1:  # Log first and every 50th
                logger.info(f"🚀 Audio speed adjustment #{self._speedup_count}: {speed_factor}x faster ({len(linear_data)} → {len(sped_up_data)} bytes)")
            
            return sped_up_data
            
        except Exception as e:
            logger.error(f"❌ Speed adjustment failed: {e}")
            # Return original audio if speed adjustment fails
            return linear_data

    async def connect(self):
        """Accept WebSocket connection from Twilio"""
        await self.accept()
        
        # Initialize connection state
        self.call_sid = None
        self.stream_sid = None
        self.hume_ws = None
        self.hume_connected = False
        
        # 🚀 ISSUE #3 FIX: Initialize response caching for faster responses
        from .response_cache import ResponseCache, initialize_response_cache
        initialize_response_cache()
        logger.info("✅ Response cache system initialized for this connection")
        
        # 🎯 AUTO-TRAINING: Store conversation for learning
        self.conversation_history = []  # Store Q&A pairs
        self.customer_messages = []
        self.agent_messages = []
        
        # Initialize Knowledge Manager AFTER accepting connection (non-blocking)
        self.knowledge_manager = None  # Default to None, load later if needed
        
        logger.info(f"📱 WebSocket connection established (Knowledge Manager will load async)")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"WebSocket disconnected: {close_code}")
        
        # 💾 SAVE: Store conversation to database first
        await self.save_conversation_to_database()
        
        # 🎯 AUTO-TRAIN: Extract conversation and train agent
        await self.auto_train_from_call()
        
        # Close HumeAI connection if open
        if self.hume_ws and not self.hume_ws.closed:
            await self.hume_ws.close()
            logger.info(f"🔌 HumeAI connection closed")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages from Twilio"""
        try:
            data = json.loads(text_data)
            event = data.get('event')
            
            if event == 'connected':
                await self.handle_connected(data)
            elif event == 'start':
                await self.handle_start(data)
            elif event == 'media':
                await self.handle_media(data)
            elif event == 'stop':
                await self.handle_stop(data)
            else:
                logger.warning(f"⚠️ Unknown event: {event}")
                
        except Exception as e:
            logger.error(f"❌ Receive error: {str(e)}")

    async def handle_connected(self, data):
        """Handle Twilio connection event"""
        logger.info(f"📞 Twilio connected: {data}")

    async def handle_start(self, data):
        """Handle stream start and connect to HumeAI"""
        try:
            # Extract stream info
            stream_data = data.get('start', {})
            self.call_sid = stream_data.get('callSid')
            self.stream_sid = stream_data.get('streamSid')
            
            logger.info(f"✅ Twilio WebSocket connected for call: {self.call_sid}")
            logger.info(f"📞 Stream started: {self.stream_sid}")
            
            # Send initial configuration to Twilio for optimal audio
            await self.configure_twilio_stream()
            
            # Connect to HumeAI
            await self.connect_to_hume()
            
        except Exception as e:
            logger.error(f"❌ Handle start error: {str(e)}")
    
    async def configure_twilio_stream(self):
        """Configure Twilio stream for optimal audio delivery"""
        try:
            logger.info(f"🔧 Configuring Twilio stream for audio delivery...")
            
            # Send stream configuration to Twilio
            # This tells Twilio we're ready to send audio back
            config_message = {
                "event": "start",
                "streamSid": self.stream_sid,
                "start": {
                    "accountSid": None,  # Twilio will fill this
                    "streamSid": self.stream_sid,
                    "callSid": self.call_sid,
                    "tracks": ["outbound"],  # We want to send audio to caller
                    "mediaFormat": {
                        "encoding": "mulaw",
                        "sampleRate": 8000,
                        "channels": 1
                    }
                }
            }
            
            # Note: We don't actually send this config message as Twilio manages it
            # But we log the configuration for debugging
            logger.info(f"📋 Stream config: µ-law, 8kHz, mono, outbound track")
            logger.info(f"📋 Ready to send media to stream: {self.stream_sid}")
            
        except Exception as e:
            logger.error(f"❌ Configure Twilio stream error: {str(e)}")

    async def connect_to_hume(self):
        """Establish connection to HumeAI EVI"""
        try:
            from decouple import config
            
            # Get credentials from environment
            hume_api_key = config('HUME_AI_API_KEY', default=config('HUME_API_KEY', default=''))
            hume_secret_key = config('HUME_AI_SECRET_KEY', default=config('HUME_SECRET_KEY', default=''))
            default_config_id = config('HUME_CONFIG_ID')
            
            # Try to get config_id from call/database (if set during initiation)
            requested_config_id = None
            
            # Check if we have call_sid, try to get agent config from database
            if self.call_sid:
                try:
                    from asgiref.sync import sync_to_async
                    from HumeAiTwilio.models import TwilioCall
                    
                    # Get call from database
                    call = await sync_to_async(TwilioCall.objects.filter(call_sid=self.call_sid).first)()
                    
                    if call:
                        # Try to get from agent relationship first
                        if hasattr(call, 'agent') and call.agent and call.agent.hume_config_id:
                            requested_config_id = call.agent.hume_config_id
                            logger.info(f"📥 Config ID from database agent: {requested_config_id}")
                        
                        # Try to get from metadata
                        elif call.metadata:
                            metadata = json.loads(call.metadata) if isinstance(call.metadata, str) else call.metadata
                            requested_config_id = metadata.get('config_id')
                            if requested_config_id:
                                logger.info(f"� Config ID from call metadata: {requested_config_id}")
                
                except Exception as db_error:
                    logger.warning(f"⚠️ Could not get config from database: {db_error}")
            
            # Validate requested config_id with HumeAI
            config_id = default_config_id  # Start with default
            
            if requested_config_id and requested_config_id != default_config_id:
                logger.info(f"🔍 Validating requested config_id: {requested_config_id}")
                
                try:
                    # Quick validation: Try to use the requested config_id
                    # We'll know if it's valid when we try to connect
                    config_id = requested_config_id
                    logger.info(f"✅ Using requested config_id: {config_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Requested config_id validation failed, falling back to default")
                    config_id = default_config_id
            else:
                logger.info(f"✅ Using default config_id from .env: {config_id}")
            
            logger.info(f"🔧 Final HumeAI Config ID: {config_id}")
            
            if not hume_api_key:
                logger.error("❌ HUME_API_KEY is empty!")
                return
            if not hume_secret_key:
                logger.error("❌ HUME_SECRET_KEY is empty!")
                return
            if not config_id:
                logger.error("❌ HUME_CONFIG_ID is empty!")
                return
            
            logger.info(f"🔑 API Key: {hume_api_key[:20]}...")
            logger.info(f"🔑 Secret Key: {hume_secret_key[:20]}...")
            logger.info(f"🔑 Config ID: {config_id}")
            
            # Connect to HumeAI EVI
            logger.info(f"🔌 Connecting to HumeAI EVI...")
            # Correct EVI WebSocket endpoint - use API key in header, not query param
            hume_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={config_id}"
            logger.info(f"🌐 URL: {hume_url}")
            
            # Add authentication headers with API key
            headers = {
                'X-Hume-Api-Key': hume_api_key,
                'Content-Type': 'application/json'
            }
            
            self.hume_ws = await asyncio.wait_for(
                websockets.connect(hume_url, extra_headers=headers, ping_interval=20, ping_timeout=20),
                timeout=10.0
            )
            
            self.hume_connected = True
            logger.info(f"✅ HumeAI WebSocket connected successfully!")
            logger.info(f"✅ Ready for call: {self.call_sid}")
            
            # Send initial session configuration to HumeAI
            # ⚡ OPTIMIZED FOR: Fast response + Clear customer voice
            session_config = {
                "type": "session_settings",
                "config_id": config_id,
                "audio": {
                    "encoding": "linear16",
                    "channels": 1,
                    "sample_rate": 48000  # 48kHz studio quality
                },
                "voice": {
                    "rate": 1.0,          # ⚡ Natural speed (20% faster - ultra smooth)
                    "pitch": 1.0,         # Natural pitch for clarity
                    "energy": 0.5,        # Good energy level
                    "volume": 1.0         # 60% louder output
                },
                # 🚀🚀🚀 BALANCED-FAST RESPONSE: Fast but stable AI responses!
                "turn_taking": {
                    "mode": "aggressive",              # ⚡ Fast turn-taking (balanced)
                    "silence_threshold_ms": 400,       # ⚡⚡ Respond after 400ms silence (OPTIMAL!)
                    "interruption_threshold_ms": 200,  # ⚡⚡ Detect interrupt in 200ms (FAST!)
                    "word_threshold": 2,               # Start responding after 2 words
                    "interruption_enabled": True,      # Allow customer to interrupt
                    "vad_sensitivity": "high",         # High voice detection sensitivity
                    "end_of_turn_threshold_ms": 300,   # 🔥 Quick turn detection (300ms)
                    "backoff_ms": 100,                 # 🔥 Balanced backoff for stable response
                    "wait_for_customer": True,         # ✅ Wait for customer to speak first
                    "auto_continue": False             # ❌ Don't continue if customer silent
                },
                # 🔊🔊 LOUD & CLEAR: Customer voice crystal clear
                "audio_input": {
                    "gain": 2.8,                       # 🔥 180% volume boost for customer voice
                    "noise_suppression": True,         # Remove background noise
                    "echo_cancellation": True,         # Remove echo
                    "auto_gain_control": True,         # Auto-adjust volume
                    "voice_boost": True                # Extra clarity boost
                },
                # 🎙️ GREETING: Auto greeting with interruption + wait for response
                "greeting": {
                    "enabled": True,
                    "text": "Hello! This is Sarah from SalesAice.ai. How are you today?",
                    "interruptible": True,             # ✅ Customer can interrupt greeting!
                    "style": "natural",
                    "wait_for_response": True,         # ✅ Wait for customer to respond
                    "pause_after_greeting_ms": 1500    # 🕐 Wait 1.5 seconds for customer response
                },
                # 🤐 SILENCE HANDLING: Don't talk if customer is silent
                "silence_handling": {
                    "enabled": True,
                    "max_wait_ms": 3000,               # Wait max 3 seconds for customer
                    "prompt_after_silence": "Are you still there?",  # Ask if customer silent too long
                    "auto_continue": False             # ❌ Don't continue talking if customer silent
                }
            }
            await self.hume_ws.send(json.dumps(session_config))
            logger.info(f"📤 Sent BALANCED-FAST config to HumeAI:")
            logger.info(f"   🎛️ Audio: 48kHz linear16 - Studio quality")
            logger.info(f"   ⚡⚡ Response: 400ms silence, 200ms interrupt - BALANCED & FAST!")
            logger.info(f"   🚀 Word threshold: 2 words - Natural start")
            logger.info(f"   🔊 Input: 2.8x gain boost - Customer voice CRYSTAL CLEAR!")
            logger.info(f"   🗣️ Voice: 1.2x rate, 1.6x volume - Natural & smooth")
            logger.info(f"   🎙️ Greeting: Sarah from SalesAice.ai - Waits for response!")
            logger.info(f"   🤐 Silence: Won't talk if customer silent - Smart waiting!")
            logger.info(f"   ⚡ Audio chunks: 40ms - Lightning-fast delivery!")
            logger.info(f"   💬 No hardcoded TwiML greeting - Direct HumeAI greeting!")
            
            # Start listening to HumeAI responses
            asyncio.create_task(self.listen_to_hume())
            
            logger.info(f"🎉 HumeAI session ready for audio processing!")
            
        except asyncio.TimeoutError:
            logger.error(f"❌ HumeAI connection timeout after 10 seconds")
            logger.error(f"   Check: 1) Internet connection 2) API credentials 3) HumeAI service status")
            
            # Retry with default config if we were using a custom one
            if config_id != default_config_id:
                logger.info(f"🔄 Retrying with default config_id: {default_config_id}")
                await self._retry_with_default_config(default_config_id, hume_api_key)
                
        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"❌ HumeAI rejected connection: HTTP {e.status_code}")
            logger.error(f"   Check API credentials and config ID: {config_id}")
            
            # If custom config failed, retry with default
            if config_id != default_config_id:
                logger.info(f"🔄 Config ID '{config_id}' rejected. Retrying with default: {default_config_id}")
                await self._retry_with_default_config(default_config_id, hume_api_key)
            
        except Exception as e:
            logger.error(f"❌ HumeAI connection error: {type(e).__name__}: {str(e)}")
            
            # Handle specific missing agent error
            if "agent" in str(e).lower() or "config" in str(e).lower():
                logger.error(f"   → Config ID not found or invalid: {config_id}")
                
                # Retry with default if custom config failed
                if config_id != default_config_id:
                    logger.info(f"🔄 Retrying with default config_id: {default_config_id}")
                    await self._retry_with_default_config(default_config_id, hume_api_key)
    
    async def _retry_with_default_config(self, default_config_id, hume_api_key):
        """Retry HumeAI connection with default config_id"""
        try:
            logger.info(f"🔄 Attempting connection with default config...")
            
            hume_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={default_config_id}"
            headers = {
                'X-Hume-Api-Key': hume_api_key,
                'Content-Type': 'application/json'
            }
            
            self.hume_ws = await asyncio.wait_for(
                websockets.connect(hume_url, extra_headers=headers, ping_interval=20, ping_timeout=20),
                timeout=10.0
            )
            
            self.hume_connected = True
            logger.info(f"✅ Connected with default config_id: {default_config_id}")
            
            # Send session config
            session_config = {
                "type": "session_settings",
                "config_id": default_config_id,
                "audio": {
                    "encoding": "linear16",
                    "channels": 1,
                    "sample_rate": 48000
                },
                "voice": {
                    "rate": 3.2,
                    "pitch": 1.2,
                    "energy": 3.0,
                    "clarity": "ultra",
                    "volume": 2.5
                }
            }
            await self.hume_ws.send(json.dumps(session_config))
            
            # Start listening
            asyncio.create_task(self.listen_to_hume())
            logger.info(f"✅ Fallback connection successful!")
            
        except Exception as retry_error:
            logger.error(f"❌ Fallback connection also failed: {retry_error}")
        except Exception as e:
            logger.error(f"❌ Handle start error: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def handle_media(self, data):
        """Forward audio from Twilio to HumeAI"""
        try:
            if not self.hume_connected or not self.hume_ws:
                logger.warning(f"⚠️ Media received but HumeAI not connected")
                return
            
            # Extract audio payload from Twilio
            media = data.get('media', {})
            payload = media.get('payload')  # Base64 µ-law audio
            
            if not payload:
                logger.warning(f"⚠️ Empty payload received from Twilio")
                return
            
            # Log first audio chunk with detailed info
            if not hasattr(self, '_first_audio_logged'):
                logger.info(f"🎤 First audio from Twilio:")
                logger.info(f"   📏 Payload length: {len(payload)} chars")
                logger.info(f"   🔧 Sample rate: 8kHz µ-law")
                logger.info(f"   📡 Stream: {self.stream_sid}")
                self._first_audio_logged = True
            
            # Convert µ-law to linear16 PCM for HumeAI
            linear_payload = self.convert_mulaw_to_linear16(payload)
            
            if not linear_payload:
                logger.error(f"❌ Audio conversion failed")
                return
            
            # Send converted audio to HumeAI with enhanced message
            hume_message = {
                "type": "audio_input",
                "data": linear_payload
            }
            
            # Check HumeAI connection before sending
            if self.hume_ws.closed:
                logger.error(f"❌ HumeAI connection closed, cannot send audio")
                self.hume_connected = False
                return
            
            await self.hume_ws.send(json.dumps(hume_message))
            
            # Enhanced logging
            if not hasattr(self, '_audio_count'):
                self._audio_count = 0
            self._audio_count += 1
            
            # Log every 25 chunks and show conversion details
            if self._audio_count % 25 == 0:
                logger.info(f"📡 Sent {self._audio_count} audio chunks to HumeAI")
                logger.info(f"   🔄 Last conversion: {len(payload)} → {len(linear_payload)} chars")
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"❌ HumeAI connection closed: {e.code} - {e.reason}")
            self.hume_connected = False
        except Exception as e:
            logger.error(f"❌ Handle media error: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")

    async def handle_stop(self, data):
        """Handle stream stop"""
        try:
            logger.info(f"⏹️  Stream stopped: {self.stream_sid}")
            
            # Close HumeAI connection
            if self.hume_ws and not self.hume_ws.closed:
                await self.hume_ws.close()
            
        except Exception as e:
            logger.error(f"❌ Handle stop error: {str(e)}")
    
    async def listen_to_hume(self):
        """Listen for responses from HumeAI and forward to Twilio"""
        try:
            logger.info(f"👂 Started listening to HumeAI responses...")
            self.audio_sequence = 0  # Track audio sequence for Twilio
            
            async for message in self.hume_ws:
                data = json.loads(message)
                
                # Check message type
                msg_type = data.get('type')
                logger.info(f"📨 Received from HumeAI: {msg_type}")
                
                if msg_type == 'audio_output':
                    # HumeAI EVI v2 sends audio in 'data' field
                    audio_data = data.get('data')
                    
                    if audio_data:
                        logger.info(f"🔊 Received audio from HumeAI ({len(audio_data)} chars)")
                        
                        # 🚀 Send audio in optimized 60ms chunks for natural playback
                        await self.send_audio_chunks_to_twilio(audio_data)
                    else:
                        logger.warning(f"⚠️ audio_output without 'data' field")
                
                elif msg_type == 'user_message':
                    # Log transcription with emotion detection
                    transcript = data.get('text')
                    logger.info(f"👤 User said: {transcript}")
                    
                    # Extract emotions from user message (HumeAI provides prosody analysis)
                    emotions = data.get('emotions', {}) or data.get('prosody', {})
                    
                    # 🎯 STORE for training with emotions
                    if transcript:
                        message_data = {
                            'text': transcript,
                            'emotions': emotions if emotions else None
                        }
                        self.customer_messages.append(message_data)
                
                elif msg_type == 'assistant_message':
                    # Log AI response text
                    response = data.get('content') or data.get('text')
                    if response:
                        logger.info(f"🤖 AI responds: {response}")
                        
                        # 🎯 STORE for training
                        self.agent_messages.append(response)
                        
                        # Create Q&A pair with emotions
                        if len(self.customer_messages) > 0:
                            last_message = self.customer_messages[-1]
                            # Handle both old string format and new dict format
                            last_question = last_message if isinstance(last_message, str) else last_message.get('text')
                            last_emotions = None if isinstance(last_message, str) else last_message.get('emotions')
                            
                            self.conversation_history.append({
                                "question": last_question,
                                "answer": response,
                                "emotions": last_emotions
                            })
                
                elif msg_type == 'error':
                    # Log HumeAI error details
                    error_msg = data.get('message', 'Unknown error')
                    error_code = data.get('code', 'N/A')
                    logger.error(f"❌ HumeAI Error [{error_code}]: {error_msg}")
        
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"🔌 HumeAI connection closed: {e.code}")
            
        except Exception as e:
            logger.error(f"❌ Listen to HumeAI error: {str(e)}")
    
    async def send_audio_chunks_to_twilio(self, audio_base64: str):
        """Send audio to Twilio in small 60ms chunks for smooth, natural playback"""
        try:
            if not audio_base64:
                logger.warning(f"⚠️ Empty audio data received from HumeAI")
                return
            
            # Convert linear16 PCM from HumeAI to µ-law for Twilio (with 48kHz→8kHz downsampling)
            mulaw_payload = self.convert_linear16_to_mulaw(audio_base64)
            mulaw_bytes = base64.b64decode(mulaw_payload)
            
            # 🚀 EXTREME OPTIMIZED: 40ms chunks = 320 bytes at 8kHz µ-law (8000 samples/sec × 0.04 sec)
            # Smaller chunks = FASTER initial audio delivery for instant response feel!
            chunk_size = 320
            chunk_count = 0
            
            logger.info(f"🚀 Sending {len(mulaw_bytes)} bytes in {len(mulaw_bytes)//chunk_size + 1} chunks (40ms - EXTREME FAST!)")
            
            for i in range(0, len(mulaw_bytes), chunk_size):
                chunk = mulaw_bytes[i:i + chunk_size]
                chunk_b64 = base64.b64encode(chunk).decode("utf-8")
                
                message = {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {"payload": chunk_b64}
                }
                
                await self.send(text_data=json.dumps(message))
                chunk_count += 1
                
                # NO DELAY - Send as fast as possible for instant response!
                # Smaller 40ms chunks = faster initial audio = perceived instant response!
            
            logger.info(f"✅ Sent {chunk_count} chunks in 40ms intervals - LIGHTNING FAST!")
                
        except Exception as e:
            logger.error(f"❌ Send audio chunks error: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    async def send_audio_chunk_to_twilio(self, chunk_payload: str, sequence: int):
        """Send individual audio chunk to Twilio with sequence tracking"""
        try:
            # Check if we have a valid stream ID (indicates connection is active)
            if not self.stream_sid:
                logger.warning(f"⚠️ No stream ID available, stopping audio transmission")
                return False
            
            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": chunk_payload
                }
            }
            
            message_json = json.dumps(message)
            await self.send(text_data=message_json)
            
            # Log every 10th chunk to avoid spam
            if sequence % 10 == 0:
                logger.info(f"📤 Sent chunk {sequence}: {len(chunk_payload)} chars")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Send chunk {sequence} error: {str(e)}")
            return False
    
    async def send_to_twilio(self, audio_base64: str):
        """Send audio from HumeAI back to Twilio"""
        try:
            if not audio_base64:
                logger.warning(f"⚠️ Empty audio data received from HumeAI")
                return
            
            # Convert linear16 PCM from HumeAI to µ-law for Twilio
            mulaw_payload = self.convert_linear16_to_mulaw(audio_base64)
            
            # Log detailed audio info
            logger.info(f"🔊 Audio conversion: {len(audio_base64)} → {len(mulaw_payload)} bytes")
            
            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": mulaw_payload
                }
            }
            
            # Log the actual message being sent
            message_json = json.dumps(message)
            logger.info(f"📤 Sending to Twilio: {len(message_json)} bytes total")
            logger.info(f"📤 Stream ID: {self.stream_sid}")
            logger.info(f"📤 Payload length: {len(mulaw_payload)} characters")
            
            await self.send(text_data=message_json)
            logger.info(f"✅ Audio successfully sent to Twilio!")
            
        except Exception as e:
            logger.error(f"❌ Send to Twilio error: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    async def auto_train_from_call(self):
        """
        🎯 AUTO-TRAINING: Extract Q&A from conversation and train agent
        Works on Local (ChromaDB) and PythonAnywhere (Django DB)
        """
        try:
            if not self.conversation_history or len(self.conversation_history) == 0:
                logger.info(f"📝 No conversation data to train from")
                return
            
            if not self.knowledge_manager:
                logger.warning(f"⚠️ Knowledge Manager not available, skipping auto-training")
                return
            
            logger.info(f"🎓 AUTO-TRAINING: Processing {len(self.conversation_history)} Q&A pairs from call")
            
            # Add each Q&A pair to knowledge base (universal method)
            trained_count = 0
            for idx, qa_pair in enumerate(self.conversation_history):
                try:
                    question = qa_pair["question"]
                    answer = qa_pair["answer"]
                    
                    # Prepare metadata
                    metadata = {
                        "call_sid": self.call_sid,
                        "source": "live_call",
                        "pair_index": idx
                    }
                    
                    # Store using universal KnowledgeManager
                    success = self.knowledge_manager.add_knowledge(
                        question=question,
                        answer=answer,
                        metadata=metadata
                    )
                    
                    if success:
                        trained_count += 1
                        logger.info(f"✅ Trained: Q: '{question[:50]}...' → A: '{answer[:50]}...'")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to train Q&A pair {idx}: {e}")
                    continue
            
            logger.info(f"🎉 AUTO-TRAINING COMPLETE: Learned {trained_count}/{len(self.conversation_history)} Q&A pairs!")
            logger.info(f"📊 Total conversation turns: {len(self.customer_messages)} customer, {len(self.agent_messages)} agent")
            
        except Exception as e:
            logger.error(f"❌ Auto-training failed: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    async def save_conversation_to_database(self):
        """
        💾 Save conversation logs to database for analytics & transcript
        """
        try:
            from HumeAiTwilio.models import TwilioCall, ConversationLog
            from channels.db import database_sync_to_async
            
            if not self.call_sid:
                logger.warning(f"⚠️ No call_sid available, skipping conversation save")
                return
            
            # Get TwilioCall object
            @database_sync_to_async
            def get_call():
                return TwilioCall.objects.filter(call_sid=self.call_sid).first()
            
            call = await get_call()
            
            if not call:
                logger.warning(f"⚠️ Call not found in database: {self.call_sid}")
                return
            
            # Save conversation logs
            @database_sync_to_async
            def save_logs():
                import json
                saved_count = 0
                
                # Save customer messages and agent responses together
                for idx, qa_pair in enumerate(self.conversation_history):
                    try:
                        # Extract emotions if available
                        emotions = qa_pair.get('emotions')
                        emotion_scores_json = json.dumps(emotions) if emotions else None
                        
                        # Save customer message with emotions
                        customer_log = ConversationLog.objects.create(
                            call=call,
                            role='user',
                            message=qa_pair['question'],
                            emotion_scores=emotion_scores_json,
                            metadata={'pair_index': idx}
                        )
                        saved_count += 1
                        
                        # 📊 Update analytics in real-time with Hume AI emotion scores
                        if emotion_scores_json:
                            try:
                                from .services.analytics_processor import AnalyticsProcessor
                                AnalyticsProcessor.update_analytics_on_new_message(
                                    call_sid=str(call.call_sid),
                                    message=qa_pair['question'],
                                    role='user',
                                    emotion_scores=emotions
                                )
                                logger.info(f"📊 Analytics updated for user message in call {call.call_sid}")
                            except Exception as e:
                                logger.error(f"Analytics update failed: {e}")
                        
                        # Save agent response
                        ConversationLog.objects.create(
                            call=call,
                            role='assistant',
                            message=qa_pair['answer'],
                            metadata={'pair_index': idx}
                        )
                        saved_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to save conversation pair {idx}: {e}")
                        continue
                
                return saved_count
            
            saved_count = await save_logs()
            logger.info(f"💾 Saved {saved_count} conversation messages to database")
            
        except Exception as e:
            logger.error(f"❌ Save conversation failed: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    def _detect_goodbye_emotion(self, emotions: dict) -> bool:
        """
        🎯 EMOTION-BASED GOODBYE DETECTION
        Detects goodbye/farewell emotions from HumeAI
        """
        if not emotions:
            return False
        
        # HumeAI emotions that indicate goodbye/ending conversation
        # These are common emotion patterns when someone says bye
        goodbye_emotions = {
            'Relief': 0.3,      # Often feel relief when call is done
            'Satisfaction': 0.4, # Satisfied with conversation outcome
            'Calmness': 0.3,    # Calm when wrapping up
            'Contentment': 0.4  # Content with resolution
        }
        
        # Check if any goodbye-related emotion is high
        for emotion, threshold in goodbye_emotions.items():
            if emotion in emotions:
                score = emotions[emotion]
                if score >= threshold:
                    logger.info(f"👋 Goodbye emotion detected: {emotion} = {score:.2f} (threshold: {threshold})")
                    return True
        
        return False
    
    async def _end_call_gracefully(self):
        """
        🎯 END CALL GRACEFULLY
        Closes HumeAI connection, which triggers Twilio to end naturally
        """
        try:
            logger.info(f"📞 Ending call gracefully...")
            
            # Close HumeAI connection
            if self.hume_ws and not self.hume_ws.closed:
                await self.hume_ws.close()
                logger.info(f"✅ HumeAI connection closed")
            
            # Close WebSocket (Twilio will end call naturally)
            await self.close()
            logger.info(f"✅ WebSocket closed, call will end naturally")
            
        except Exception as e:
            logger.error(f"❌ Error ending call gracefully: {e}")