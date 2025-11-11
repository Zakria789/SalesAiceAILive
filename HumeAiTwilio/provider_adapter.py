"""
🎙️ PROVIDER ADAPTER - Support Both Twilio & Vonage
Abstraction layer that converts provider-specific data to unified format
Keeps WebSocket and HumeAI logic provider-agnostic
"""

import json
import base64
import logging
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from decouple import config

logger = logging.getLogger(__name__)


class ProviderAdapter:
    """
    Abstract interface for voice providers
    Converts Twilio/Vonage data to unified format
    """
    
    @staticmethod
    def detect_provider_from_call_sid(call_id: str) -> str:
        """
        Detect provider based on call ID format
        - Twilio: Starts with 'CA' (e.g., CA123456...)
        - Vonage: UUID format (e.g., 12345678-1234-...)
        """
        if call_id.startswith('CA'):
            return 'twilio'
        elif '-' in call_id:
            return 'vonage'
        else:
            # Default to environment setting
            return config('VOICE_PROVIDER', default='twilio')
    
    @staticmethod
    def get_provider_from_db(call_sid: str) -> Optional[str]:
        """Get provider from database TwilioCall record"""
        try:
            from .models import TwilioCall
            call = TwilioCall.objects.filter(call_sid=call_sid).values_list('provider', flat=True).first()
            return call
        except Exception as e:
            logger.warning(f"Could not get provider from DB: {e}")
            return None
    
    @staticmethod
    def normalize_call_data(provider: str, raw_data: Dict) -> Dict:
        """
        Convert provider-specific data to unified format
        
        Twilio format:
        {
            "event": "media",
            "streamSid": "...",
            "media": {
                "payload": "..."  # base64 µ-law audio
            }
        }
        
        Vonage format:
        {
            "uuid": "...",
            "status": "answered",
            "audio": "..."  # base64 linear16 audio
        }
        
        Returns unified format:
        {
            "type": "audio_data",
            "provider": "twilio|vonage",
            "call_id": "...",
            "stream_id": "...",
            "audio_data": "...",  # base64
            "encoding": "mulaw|linear16",
            "sample_rate": 8000|16000,
            "original": {...}
        }
        """
        try:
            if provider == 'twilio':
                return ProviderAdapter._normalize_twilio_data(raw_data)
            elif provider == 'vonage':
                return ProviderAdapter._normalize_vonage_data(raw_data)
            else:
                logger.warning(f"Unknown provider: {provider}")
                return {}
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            return {}
    
    @staticmethod
    def _normalize_twilio_data(data: Dict) -> Dict:
        """Convert Twilio format to unified"""
        try:
            event = data.get('event')
            
            if event == 'media':
                media = data.get('media', {})
                return {
                    'type': 'audio_data',
                    'provider': 'twilio',
                    'call_id': data.get('start', {}).get('callSid') or cache.get('current_call_sid'),
                    'stream_id': data.get('streamSid'),
                    'audio_data': media.get('payload'),
                    'encoding': 'mulaw',
                    'sample_rate': 8000,
                    'original': data
                }
            elif event == 'start':
                return {
                    'type': 'stream_start',
                    'provider': 'twilio',
                    'call_id': data.get('start', {}).get('callSid'),
                    'stream_id': data.get('start', {}).get('streamSid'),
                    'original': data
                }
            elif event == 'stop':
                return {
                    'type': 'stream_stop',
                    'provider': 'twilio',
                    'stream_id': data.get('streamSid'),
                    'original': data
                }
            else:
                return {
                    'type': 'unknown',
                    'provider': 'twilio',
                    'event': event,
                    'original': data
                }
        except Exception as e:
            logger.error(f"Error normalizing Twilio data: {e}")
            return {}
    
    @staticmethod
    def _normalize_vonage_data(data: Dict) -> Dict:
        """Convert Vonage format to unified"""
        try:
            # Check if it's a stream callback or event callback
            if 'audio' in data:
                # Stream callback - raw audio data
                return {
                    'type': 'audio_data',
                    'provider': 'vonage',
                    'call_id': data.get('uuid'),
                    'stream_id': data.get('uuid'),  # Vonage uses uuid for both
                    'audio_data': data.get('audio'),
                    'encoding': 'linear16',  # Vonage sends linear16
                    'sample_rate': 16000,  # Vonage 16kHz
                    'original': data
                }
            else:
                # Event callback - status update
                status = data.get('status', 'unknown')
                return {
                    'type': f'call_{status}',
                    'provider': 'vonage',
                    'call_id': data.get('uuid'),
                    'status': status,
                    'original': data
                }
        except Exception as e:
            logger.error(f"Error normalizing Vonage data: {e}")
            return {}
    
    @staticmethod
    def convert_audio_format(
        audio_data: str,  # base64
        from_format: str,  # 'mulaw' or 'linear16'
        to_format: str    # target format
    ) -> str:
        """
        Convert audio between formats
        Handles:
        - Twilio µ-law 8kHz → Vonage linear16 16kHz
        - Vonage linear16 16kHz → Twilio µ-law 8kHz
        """
        try:
            if from_format == to_format:
                return audio_data  # No conversion needed
            
            import audioop
            
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
            
            if from_format == 'mulaw' and to_format == 'linear16':
                # Twilio → Vonage: µ-law 8kHz → linear16 16kHz
                # Convert µ-law to linear16 (8kHz)
                linear16_8k = audioop.ulaw2lin(audio_bytes, 2)
                
                # Upsample 8kHz → 16kHz
                linear16_16k = audioop.ratecv(linear16_8k, 2, 1, 8000, 16000, None)[0]
                
                logger.debug(f"Audio conversion: µ-law 8kHz ({len(audio_bytes)} bytes) → linear16 16kHz ({len(linear16_16k)} bytes)")
                return base64.b64encode(linear16_16k).decode('utf-8')
            
            elif from_format == 'linear16' and to_format == 'mulaw':
                # Vonage → Twilio: linear16 16kHz → µ-law 8kHz
                # Downsample 16kHz → 8kHz
                linear16_8k = audioop.ratecv(audio_bytes, 2, 1, 16000, 8000, None)[0]
                
                # Convert linear16 to µ-law
                mulaw_8k = audioop.lin2ulaw(linear16_8k, 2)
                
                logger.debug(f"Audio conversion: linear16 16kHz ({len(audio_bytes)} bytes) → µ-law 8kHz ({len(mulaw_8k)} bytes)")
                return base64.b64encode(mulaw_8k).decode('utf-8')
            
            else:
                logger.warning(f"Unsupported conversion: {from_format} → {to_format}")
                return audio_data
        
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return audio_data
    
    @staticmethod
    def create_provider_stream_message(
        provider: str,
        audio_data: str,  # base64
        call_id: str,
        stream_id: Optional[str] = None
    ) -> str:
        """
        Create provider-specific message to send audio back to caller
        
        Twilio format:
        {
            "event": "media",
            "streamSid": "...",
            "media": {
                "payload": "..."
            }
        }
        
        Vonage format:
        {
            "action": "input",
            "audio": "..."
        }
        """
        try:
            if provider == 'twilio':
                return json.dumps({
                    'event': 'media',
                    'streamSid': stream_id or call_id,
                    'media': {
                        'payload': audio_data
                    }
                })
            
            elif provider == 'vonage':
                return json.dumps({
                    'action': 'input',
                    'uuid': call_id,
                    'audio': audio_data
                })
            
            else:
                logger.warning(f"Unknown provider: {provider}")
                return json.dumps({'error': 'Unknown provider'})
        
        except Exception as e:
            logger.error(f"Error creating stream message: {e}")
            return json.dumps({'error': str(e)})
    
    @staticmethod
    def extract_call_id_from_webhook(provider: str, data: Dict) -> Optional[str]:
        """Extract call ID from provider webhook data"""
        try:
            if provider == 'twilio':
                # Try different sources
                call_id = data.get('start', {}).get('callSid')
                if not call_id:
                    call_id = data.get('CallSid')
                return call_id
            
            elif provider == 'vonage':
                return data.get('uuid')
            
            else:
                return None
        except Exception as e:
            logger.error(f"Error extracting call_id: {e}")
            return None
    
    @staticmethod
    def cache_provider_info(call_id: str, provider: str, additional_data: Optional[Dict] = None):
        """Store provider info in cache for quick lookup"""
        try:
            cache_key = f'provider_info_{call_id}'
            cache_data = {
                'provider': provider,
                'detected_at': timezone.now().isoformat(),
            }
            
            if additional_data:
                cache_data.update(additional_data)
            
            cache.set(cache_key, cache_data, timeout=3600)  # 1 hour
            logger.debug(f"Cached provider info: {call_id} → {provider}")
        except Exception as e:
            logger.warning(f"Could not cache provider info: {e}")
    
    @staticmethod
    def get_cached_provider_info(call_id: str) -> Optional[Dict]:
        """Retrieve provider info from cache"""
        try:
            cache_key = f'provider_info_{call_id}'
            return cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Could not get cached provider info: {e}")
            return None


class CallDataNormalizer:
    """Normalize call data from different providers to unified format"""
    
    @staticmethod
    def normalize_call_record(provider: str, raw_call_data: Dict) -> Dict:
        """
        Convert provider-specific call record to unified format
        
        Returns:
        {
            'call_id': '...',
            'from_number': '+1234567890',
            'to_number': '+1234567890',
            'status': 'completed',
            'duration': 125,
            'started_at': '2025-10-29T...',
            'ended_at': '2025-10-29T...',
            'recording_url': '...',
            'metadata': {...}
        }
        """
        try:
            if provider == 'twilio':
                return CallDataNormalizer._normalize_twilio_call(raw_call_data)
            elif provider == 'vonage':
                return CallDataNormalizer._normalize_vonage_call(raw_call_data)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error normalizing call record: {e}")
            return {}
    
    @staticmethod
    def _normalize_twilio_call(data: Dict) -> Dict:
        """Normalize Twilio call record"""
        return {
            'provider': 'twilio',
            'call_id': data.get('CallSid'),
            'from_number': data.get('From'),
            'to_number': data.get('To'),
            'status': data.get('CallStatus', '').lower(),
            'duration': int(data.get('CallDuration', 0)),
            'recording_url': data.get('RecordingUrl'),
            'raw': data
        }
    
    @staticmethod
    def _normalize_vonage_call(data: Dict) -> Dict:
        """Normalize Vonage call record"""
        return {
            'provider': 'vonage',
            'call_id': data.get('uuid'),
            'from_number': data.get('from'),
            'to_number': data.get('to'),
            'status': data.get('status', '').lower(),
            'duration': int(data.get('duration', 0)),
            'recording_url': data.get('recording_url'),
            'raw': data
        }


# Import timezone at the end to avoid circular imports
from django.utils import timezone
