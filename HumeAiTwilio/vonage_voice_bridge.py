"""
🎙️ VONAGE VOICE BRIDGE FOR HUMEAI
Complete integration for real phone call testing with HumeAI agents via Vonage
Provider replacement for twilio_voice_bridge.py
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.utils import timezone
from decouple import config
import logging
import json
from vonage import Auth, Vonage

logger = logging.getLogger(__name__)

# Vonage config
VONAGE_API_KEY = config('VONAGE_API_KEY', default='')
VONAGE_API_SECRET = config('VONAGE_API_SECRET', default='')
VONAGE_APPLICATION_ID = config('VONAGE_APPLICATION_ID', default='')
VONAGE_PRIVATE_KEY_PATH = config('VONAGE_PRIVATE_KEY_PATH', default='./private_key.pem')
VONAGE_PHONE_NUMBER = config('VONAGE_PHONE_NUMBER', default='')

# HumeAI config - Support both variable names
HUME_AI_API_KEY = config('HUME_AI_API_KEY', default=config('HUME_API_KEY', default=''))
HUME_API_KEY = HUME_AI_API_KEY  # Alias
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')

# Your server URL (for webhooks)
SERVER_URL = config('SERVER_URL', default='http://127.0.0.1:8000')
BASE_URL = config('BASE_URL', default=SERVER_URL)

# Initialize Vonage client with JWT (Voice API requires it)
try:
    import os
    
    # Check if we have application_id and private key for Voice API
    if VONAGE_APPLICATION_ID and os.path.exists(VONAGE_PRIVATE_KEY_PATH):
        logger.info("🔐 Initializing Vonage with JWT auth (Voice API)...")
        
        # Read private key as text (not bytes)
        with open(VONAGE_PRIVATE_KEY_PATH, 'r') as key_file:
            private_key = key_file.read()
            logger.info(f"   ✅ Private key loaded: {len(private_key)} bytes")
        
        # Create Auth with FULL credentials (api_key, api_secret, application_id, private_key)
        vonage_auth = Auth(
            api_key=VONAGE_API_KEY,
            api_secret=VONAGE_API_SECRET,
            application_id=VONAGE_APPLICATION_ID,
            private_key=private_key
        )
        
        vonage_client = Vonage(vonage_auth)
        logger.info(f"✅ Vonage client initialized with JWT (App: {VONAGE_APPLICATION_ID[:8]}...)")
        
    else:
        # Fallback to basic auth (won't work for Voice API but won't crash)
        logger.warning("⚠️  No APPLICATION_ID or private key found - using basic auth (Voice API won't work!)")
        logger.warning(f"   Set VONAGE_APPLICATION_ID and VONAGE_PRIVATE_KEY_PATH in .env")
        
        vonage_auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)
        vonage_client = Vonage(vonage_auth)
        logger.info("✅ Vonage client initialized (basic auth - SMS only)")
        
except Exception as e:
    logger.error(f"❌ Failed to initialize Vonage client: {e}", exc_info=True)
    vonage_client = None


@csrf_exempt
@require_POST
def vonage_voice_webhook(request):
    """
    Vonage Voice Webhook - Handles incoming calls
    This is called when someone calls your Vonage number
    
    Vonage sends call events as JSON POST requests
    """
    try:
        # Parse request body as JSON
        body = json.loads(request.body) if request.body else {}
        
        # Vonage call event details
        uuid = body.get('uuid', 'Unknown')  # Vonage call UUID (equivalent to Twilio call_sid)
        from_number = body.get('from', 'Unknown')
        to_number = body.get('to', 'Unknown')
        call_event = body.get('call_event', 'Unknown')  # ringing, answered, completed
        
        logger.info(f"📞 Vonage incoming call event: {call_event} | UUID: {uuid} | {from_number} → {to_number}")
        
        # Only process 'answered' event (equivalent to Twilio's voice webhook)
        if call_event != 'answered':
            logger.info(f"ℹ️  Ignoring {call_event} event - only processing answered calls")
            return JsonResponse({'status': 'ignored'})
        
        # Create TwilioCall record in database (reuse same model for simplicity)
        # Note: We'll use vonage_uuid in the call_sid field for now
        from .models import TwilioCall, HumeAgent
        
        # Get default agent for this call
        default_agent = None
        try:
            # Try to get the first active agent (status='active')
            default_agent = HumeAgent.objects.filter(status='active').first()
            if not default_agent:
                # Fallback: get any agent
                default_agent = HumeAgent.objects.first()
            if default_agent:
                logger.info(f"✅ Using default HumeAI agent: {default_agent.name} (Config: {default_agent.hume_config_id})")
        except Exception as e:
            logger.warning(f"⚠️  Could not get default agent: {e}")
        
        call = TwilioCall.objects.create(
            call_sid=uuid,  # Use Vonage UUID as call_sid
            from_number=from_number,
            to_number=to_number,
            direction='inbound',  # ✅ This is an incoming call
            status='answered',
            provider='vonage',  # Track provider
            started_at=timezone.now(),
            agent=default_agent  # ✅ ASSIGN AGENT SO HUME CONNECTS!
        )
        
        if default_agent:
            logger.info(f"✅ Created TwilioCall record: {call.id} with agent: {default_agent.name} (Vonage UUID: {uuid})")
        else:
            logger.warning(f"⚠️  Created TwilioCall record WITHOUT agent: {call.id} - HumeAI won't connect!")
        
        # Store Vonage UUID in cache for later reference in WebSocket consumer
        from django.core.cache import cache
        cache.set(f'vonage_uuid_{uuid}', uuid, timeout=600)  # 10 minutes
        
        # Return NCCOv2 (Vonage Call Control) response with WebSocket stream
        # This tells Vonage how to handle the call
        ws_url = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')
        
        ncco = [
            {
                "action": "stream",
                "streamUrl": [f"{ws_url}/ws/vonage-stream/{uuid}"],
                "eventWebhook": {
                    "url": f"{BASE_URL}/api/hume-twilio/vonage-event-callback/",
                    "method": "POST"
                }
            }
        ]
        
        logger.info(f"✅ NCCO response generated for call {uuid}")
        
        return JsonResponse(ncco, safe=False, content_type='application/json')
    
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in Vonage webhook request")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"❌ Error in vonage_voice_webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def vonage_outgoing_answer_webhook(request):
    """
    🎙️ Vonage Answer Webhook for OUTGOING Calls (from API call initiation)
    
    Called when an OUTGOING call is answered.
    Returns NCCO with WebSocket stream URL to connect to HumeAI.
    
    This is the answer_url callback set in call_initiation.py
    
    ✅ Accepts both GET and POST (Vonage sends answer_url as GET request)
    """
    try:
        # Import config at function level
        from decouple import config
        
        # Get API keys from .env
        HUME_API_KEY = config('HUME_API_KEY', default='')
        HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')
        BASE_URL = config('BASE_URL', default=config('SERVER_URL', default='http://127.0.0.1:8000'))
        
        # Parse query params (Vonage sends call details in query string for answer_url)
        from_param = request.GET.get('from', '')
        to_param = request.GET.get('to', '')
        uuid = request.GET.get('uuid', 'Unknown')
        conversation_uuid = request.GET.get('conversation_uuid', '')
        
        logger.info(f"[CALL] OUTGOING call answered: {uuid}")
        logger.info(f"   From: {from_param}, To: {to_param}")
        
        # Get the call from database
        from .models import TwilioCall
        try:
            call = TwilioCall.objects.get(call_sid=uuid)
            logger.info(f"[OK] Found call record: {call.id}")
            logger.info(f"   Agent: {call.agent.name if call.agent else 'None'}")
            logger.info(f"   HumeAI Config: {call.agent.hume_config_id if call.agent else 'None'}")
            
            # SET started_at timestamp when answer webhook is called
            if not call.started_at:
                call.started_at = timezone.now()
                call.save()
                logger.info(f"[OK] Set call started_at timestamp")
        except TwilioCall.DoesNotExist:
            logger.warning(f"[WARNING] Call not found: {uuid}")
            call = None
        
        # Get HumeAI config from call or use default
        hume_config_id = HUME_CONFIG_ID  # Default from .env
        if call and call.agent and call.agent.hume_config_id:
            hume_config_id = call.agent.hume_config_id
            logger.info(f"[OK] Using agent's config: {hume_config_id}")
        elif call and call.hume_config_id:
            hume_config_id = call.hume_config_id
            logger.info(f"[OK] Using call's config: {hume_config_id}")
        else:
            logger.info(f"[INFO] Using default config from .env: {hume_config_id}")
        
        # [FIX] DIRECT HUME AI CONNECTION with proper auth
        # Build HumeAI WebSocket URL with API key in URL (Vonage NCCO doesn't support headers)
        # HumeAI expects: wss://api.hume.ai/v0/assistant/chat?config_id=xxx&api_key=xxx
        hume_ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={hume_config_id}&api_key={HUME_API_KEY}"
        
        logger.info(f"[CONNECT] Direct HumeAI WebSocket for call {uuid}")
        logger.info(f"   Config: {hume_config_id}")
        logger.info(f"   API Key in URL (NCCO limitation)")
        
        # REAL-TIME SOLUTION: Use "connect" action with WebSocket endpoint
        # This establishes bidirectional audio stream (Vonage <-> Server <-> HumeAI)
        # Vonage sends audio as base64 in WebSocket messages
        # We relay to HumeAI and send responses back
        
        server_ws_url = f"wss://uncontortioned-na-ponderously.ngrok-free.dev/api/vonage-stream/{uuid}/"
        
        ncco = [
            {
                "action": "connect",
                "endpoint": [
                    {
                        "type": "websocket",
                        "uri": server_ws_url,
                        "content-type": "audio/l16;rate=16000"
                    }
                ]
            }
        ]
        
        logger.info(f"[REAL-TIME] Using connect + websocket for bidirectional audio")
        logger.info(f"[DEBUG] WebSocket URL: {server_ws_url}")
        logger.info(f"[DEBUG] FULL NCCO JSON: {json.dumps(ncco, indent=2)}")
        return JsonResponse(ncco, safe=False, content_type='application/json')
        
    except Exception as e:
        logger.error(f"❌ Error in vonage_outgoing_answer_webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def vonage_event_callback(request):
    """
    Vonage Event Callback - Handles call status updates
    Called when call events occur: answered, ringing, completed, etc.
    
    ⚠️ IMPORTANT: Also handles "answered" event to return NCCO stream setup
    (In case answer_url webhook is not called)
    """
    try:
        body = json.loads(request.body) if request.body else {}
        
        uuid = body.get('uuid', 'Unknown')  # Call UUID
        status = body.get('status', 'Unknown')  # Event type
        from_number = body.get('from', 'Unknown')
        to_number = body.get('to', 'Unknown')
        
        logger.info(f"📊 Vonage event callback: {status} for UUID: {uuid}")
        logger.info(f"🔍 Full webhook body: {json.dumps(body, indent=2)}")  # DEBUG
        
        from .models import TwilioCall
        
        # ✅ UPDATED: Event callback should NOT return NCCO
        # NCCO is already returned from answer_url (vonage-outgoing-answer)
        # Event callback is ONLY for status updates, not for returning NCCO
        # Vonage gets confused if multiple endpoints return different NCCOs!
        if status.lower() == 'answered':
            logger.info(f"📞 ANSWERED event detected - Updating status only (no NCCO)")
            
            try:
                call = TwilioCall.objects.get(call_sid=uuid)
                logger.info(f"✅ Found existing call record: {call.id}")
                
                # Update status to in_progress (call is active)
                call.status = 'in_progress'  # ✅ Set to in_progress for live tracking
                if not call.started_at:
                    call.started_at = timezone.now()
                call.save()
                logger.info(f"✅ Updated call {uuid} status to in_progress")
                
                # Return simple OK - no NCCO!
                return JsonResponse({'status': 'ok'})
                
            except TwilioCall.DoesNotExist:
                logger.warning(f"⚠️  Call {uuid} not found - NCCO already returned from answer_url")
                return JsonResponse({'status': 'ok'})
        
        # Handle other events (ringing, started, completed, etc.)
        try:
            call = TwilioCall.objects.get(call_sid=uuid)
            
            # Map Vonage status to our status
            # ✅ IMPORTANT: Map 'answered' to 'in_progress' for live updates
            status_mapping = {
                'started': 'ringing',
                'ringing': 'ringing',
                'answered': 'in_progress',  # ✅ Active call
                'completed': 'completed',
                'failed': 'failed',
                'busy': 'failed',
                'cancelled': 'failed',
                'timeout': 'failed'
            }
            
            mapped_status = status_mapping.get(status.lower(), status.lower())
            call.status = mapped_status
            
            # Handle completed call
            if status.lower() == 'completed':
                call.ended_at = timezone.now()
                if call.started_at:
                    call.duration = int((call.ended_at - call.started_at).total_seconds())
                
                # 🔥 AUTO-GENERATE ANALYTICS when call completes
                from .services.analytics_processor import AnalyticsProcessor
                import threading
                thread = threading.Thread(
                    target=AnalyticsProcessor.process_completed_call,
                    args=(uuid,)
                )
                thread.daemon = True
                thread.start()
                logger.info(f"🚀 Started analytics processing for call {uuid}")
            
            call.save()
            logger.info(f"✅ Updated call {uuid} status to {status}")
            
            # DISABLED: Intelligent scheduling (customer_profile field missing)
            # TODO: Re-enable after adding customer_profile to CallSession model
            # if status.lower() == 'completed':
            #     from .intelligent_hume_scheduler import hume_twilio_scheduler
            #     try:
            #         scheduling_result = hume_twilio_scheduler.analyze_hume_call_and_schedule(call)
            #         if scheduling_result['success']:
            #             logger.info(f"✅ Auto-scheduled next call: {scheduling_result['analyzed_outcome']}")
            #     except Exception as e:
            #         logger.warning(f"⚠️  Scheduling failed (non-blocking): {e}")
        
        except TwilioCall.DoesNotExist:
            logger.warning(f"⚠️  Call {uuid} not found in database")
        
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"❌ Error in vonage_event_callback: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def vonage_stream_callback(request):
    """
    Vonage Stream Callback - Receives audio stream data
    This is where we receive raw audio from the caller
    
    We convert this to HumeAI WebSocket format
    """
    try:
        body = json.loads(request.body) if request.body else {}
        
        uuid = body.get('uuid', 'Unknown')
        audio_data = body.get('audio', None)
        
        if audio_data:
            logger.debug(f"📨 Received audio stream chunk from Vonage call {uuid}")
            
            # Store in cache or queue for WebSocket consumer
            from django.core.cache import cache
            
            # Add to queue for HumeAI consumer
            queue_key = f'vonage_audio_queue_{uuid}'
            current_queue = cache.get(queue_key, [])
            current_queue.append(audio_data)
            cache.set(queue_key, current_queue[-100:], timeout=60)  # Keep last 100 chunks
        
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"❌ Error in vonage_stream_callback: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_GET
def vonage_health_check(request):
    """
    Health check endpoint for Vonage webhooks
    Use this to verify your webhook configuration
    """
    try:
        vonage_status = "✅ OK" if vonage_client else "❌ Client Not Initialized"
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'Vonage Voice Bridge',
            'vonage_client': vonage_status,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


def initiate_vonage_call(to_number, from_number=None, agent_id=None):
    """
    Initiate an outbound call via Vonage
    
    Args:
        to_number: Recipient phone number
        from_number: Caller ID (defaults to VONAGE_PHONE_NUMBER)
        agent_id: AI agent to use for this call
    
    Returns:
        dict: Call status and UUID
    """
    if not vonage_client:
        logger.error("❌ Vonage client not initialized")
        return {'success': False, 'error': 'Vonage client not available'}
    
    try:
        from_number = from_number or VONAGE_PHONE_NUMBER
        
        # Create database record
        from .models import TwilioCall, HumeAgent
        
        # Get agent if specified
        agent = None
        if agent_id:
            try:
                agent = HumeAgent.objects.get(id=agent_id)
            except HumeAgent.DoesNotExist:
                logger.warning(f"⚠️  Agent {agent_id} not found, using default")
        
        # If no specific agent, get default
        if not agent:
            try:
                agent = HumeAgent.objects.filter(status='active').first()
                if not agent:
                    agent = HumeAgent.objects.first()
                if agent:
                    logger.info(f"✅ Using default HumeAI agent: {agent.name}")
            except Exception as e:
                logger.warning(f"⚠️  Could not get default agent: {e}")
        
        # Build WebSocket URL for streaming
        ws_url = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')
        
        # Strip country code from numbers for Vonage API
        to_clean = to_number.lstrip('+')
        from_clean = from_number.lstrip('+')
        
        # Initiate Vonage call via REST API
        # Use answer_url and event_url for proper webhook flow
        # Updated for Vonage SDK v3+
        call_data = {
            "to": [{"type": "phone", "number": to_clean}],
            "from": {"type": "phone", "number": from_clean},
            "answer_url": [f"{BASE_URL}/api/hume-twilio/vonage-voice-webhook/"],
            "event_url": [f"{BASE_URL}/api/hume-twilio/vonage-event-callback/"]
        }
        
        response = vonage_client.voice.create_call(call_data)
        
        call_uuid = response.uuid
        
        # Create call record
        call = TwilioCall.objects.create(
            call_sid=call_uuid,
            from_number=from_number,
            to_number=to_number,
            direction='outbound',  # ✅ This is an outgoing call we initiated
            agent=agent,
            status='initiated',
            provider='vonage',
            started_at=timezone.now()
        )
        
        logger.info(f"✅ Initiated Vonage call {call_uuid} → {to_number}")
        
        return {
            'success': True,
            'call_uuid': call_uuid,
            'call_id': call.id,
            'from': from_number,
            'to': to_number,
            'status': 'initiated'
        }
    
    except Exception as e:
        logger.error(f"❌ Error initiating Vonage call: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def get_vonage_call_status(call_uuid):
    """
    Get call status from Vonage
    
    Args:
        call_uuid: Vonage call UUID
    
    Returns:
        dict: Call details
    """
    if not vonage_client:
        return {'error': 'Vonage client not available'}
    
    try:
        from .models import TwilioCall
        
        call = TwilioCall.objects.get(call_sid=call_uuid)
        
        return {
            'call_uuid': call_uuid,
            'status': call.status,
            'from': call.from_number,
            'to': call.to_number,
            'duration': call.duration or 0,
            'started_at': call.started_at.isoformat() if call.started_at else None,
            'ended_at': call.ended_at.isoformat() if call.ended_at else None,
        }
    
    except TwilioCall.DoesNotExist:
        logger.warning(f"⚠️  Call {call_uuid} not found")
        return {'error': 'Call not found'}
    except Exception as e:
        logger.error(f"❌ Error getting call status: {e}")
        return {'error': str(e)}
