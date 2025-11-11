"""
🎯 CALL INITIATION API
======================

Initiate calls with agent selection, customer info, and real-time status
"""

import json
import logging
from datetime import datetime
from typing import Optional

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from decouple import config
from twilio.rest import Client

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR TRANSCRIPT FORMATTING
# ═══════════════════════════════════════════════════════════

def _format_transcript(conversation_logs):
    """
    Format conversation logs into structured transcript with timestamps
    """
    formatted = []
    for log in conversation_logs:
        formatted.append({
            'timestamp': log.get('timestamp', ''),
            'speaker': '🤖 AI Agent' if log.get('role') == 'agent' else '👤 Customer',
            'role': log.get('role'),
            'message': log.get('message'),
            'emotions': log.get('emotions', []),
            'sentiment': log.get('sentiment')
        })
    return formatted


def _generate_plain_transcript(conversation_logs):
    """
    Generate plain text transcript for easy reading/export
    """
    lines = []
    for log in conversation_logs:
        speaker = 'AI Agent' if log.get('role') == 'agent' else 'Customer'
        timestamp = log.get('timestamp', '')
        message = log.get('message', '')
        lines.append(f"[{timestamp}] {speaker}: {message}")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# VOICE PROVIDER CONFIGURATION
# ═══════════════════════════════════════════════════════════
VOICE_PROVIDER = config('VOICE_PROVIDER', default='twilio')

# Twilio Configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Vonage Configuration
VONAGE_API_KEY = config('VONAGE_API_KEY', default='')
VONAGE_API_SECRET = config('VONAGE_API_SECRET', default='')
VONAGE_APPLICATION_ID = config('VONAGE_APPLICATION_ID', default='')
VONAGE_PRIVATE_KEY_PATH = config('VONAGE_PRIVATE_KEY_PATH', default='')
VONAGE_PHONE_NUMBER = config('VONAGE_PHONE_NUMBER', default='')

BASE_URL = config('BASE_URL', default='https://uncontortioned-na-ponderously.ngrok-free.dev')

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    logger.warning(f"⚠️ Twilio client initialization warning: {e}")
    twilio_client = None

# Initialize Vonage client
vonage_client = None
try:
    from vonage import Auth, Vonage
    import os
    
    logger.info(f"🔍 Vonage initialization check:")
    logger.info(f"   API_KEY set: {bool(VONAGE_API_KEY)}")
    logger.info(f"   API_SECRET set: {bool(VONAGE_API_SECRET)}")
    logger.info(f"   APP_ID set: {bool(VONAGE_APPLICATION_ID)}")
    logger.info(f"   PRIVATE_KEY_PATH: {VONAGE_PRIVATE_KEY_PATH}")
    logger.info(f"   Private key file exists: {os.path.exists(VONAGE_PRIVATE_KEY_PATH) if VONAGE_PRIVATE_KEY_PATH else False}")
    
    # Voice API REQUIRES JWT auth with Application ID + Private Key (content, not path!)
    if VONAGE_APPLICATION_ID and VONAGE_PRIVATE_KEY_PATH and os.path.exists(VONAGE_PRIVATE_KEY_PATH):
        try:
            logger.info(f"📝 Attempting JWT auth with app_id: {VONAGE_APPLICATION_ID}")
            
            # Read the private key file content
            with open(VONAGE_PRIVATE_KEY_PATH, 'r') as f:
                private_key_content = f.read()
            
            logger.info(f"   Private key loaded from file (length: {len(private_key_content)} bytes)")
            
            # Auth MUST include api_key, api_secret, application_id, AND private_key content!
            vonage_auth = Auth(
                api_key=VONAGE_API_KEY,
                api_secret=VONAGE_API_SECRET,
                application_id=VONAGE_APPLICATION_ID,
                private_key=private_key_content
            )
            vonage_client = Vonage(vonage_auth)
            logger.info("✅ Vonage client initialized (JWT auth with full credentials) SUCCESS!")
        except Exception as jwt_error:
            logger.error(f"❌ JWT auth failed: {jwt_error}")
            logger.error(f"   Error type: {type(jwt_error).__name__}")
            import traceback
            logger.error(traceback.format_exc())
    else:
        logger.warning("⚠️ Vonage Voice API requires:")
        logger.warning(f"   VONAGE_APPLICATION_ID: {bool(VONAGE_APPLICATION_ID)}")
        logger.warning(f"   VONAGE_PRIVATE_KEY_PATH file exists: {os.path.exists(VONAGE_PRIVATE_KEY_PATH) if VONAGE_PRIVATE_KEY_PATH else False}")
except Exception as e:
    logger.error(f"❌ Vonage client initialization error: {e}")
    import traceback
    logger.error(traceback.format_exc())


# ═══════════════════════════════════════════════════════════
# AVAILABLE AGENTS CONFIGURATION
# ═══════════════════════════════════════════════════════════

AVAILABLE_AGENTS = {
    "sarah_sales": {
        "name": "Sarah - Sales Agent",
        "config_id": config('HUME_CONFIG_ID', default='13624648-658a-49b1-81cb-a0f2e2b05de5'),
        "voice": "ITO",
        "model": "Claude 3.5 Sonnet",
        "specialty": "Sales & lead generation",
        "description": "Expert in cold calling, objection handling, and closing deals"
    },
    "alex_support": {
        "name": "Alex - Support Agent",
        "config_id": config('HUME_SUPPORT_CONFIG_ID', default=''),
        "voice": "Inspiring Woman",
        "model": "Claude 3.5 Sonnet",
        "specialty": "Customer support",
        "description": "Handles customer inquiries, troubleshooting, and technical support"
    },
    "emma_onboarding": {
        "name": "Emma - Onboarding Agent",
        "config_id": config('HUME_ONBOARDING_CONFIG_ID', default=''),
        "voice": "ITO",
        "model": "Claude 3.5 Sonnet",
        "specialty": "Customer onboarding",
        "description": "Guides new customers through setup and initial training"
    }
}


# ═══════════════════════════════════════════════════════════
# API 1: GET AVAILABLE AGENTS
# ═══════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def get_available_agents(request):
    """
    Get list of available AI agents from database and hardcoded
    
    GET /api/hume-twilio/agents-list/
    
    Response:
    {
        "success": true,
        "database_agents": [...],
        "hardcoded_agents": [...]
    }
    """
    try:
        # Get database agents
        db_agents = []
        try:
            from HumeAiTwilio.models import HumeAgent
            agents_qs = HumeAgent.objects.filter(status='active').order_by('created_at')
            
            for idx, agent in enumerate(agents_qs):
                db_agents.append({
                    'id': idx + 1,  # Numeric ID for easy API calls
                    'uuid': str(agent.id),
                    'name': agent.name,
                    'voice': agent.voice_name,
                    'language': agent.language,
                    'status': agent.status,
                    'has_config': bool(agent.hume_config_id),
                    'config_id': agent.hume_config_id,
                    'description': agent.description or agent.system_prompt[:100] + '...'
                })
        except Exception as e:
            logger.error(f"Error fetching database agents: {e}")
        
        # Get hardcoded agents
        hardcoded_agents = []
        for agent_id, agent_info in AVAILABLE_AGENTS.items():
            # Only include agents with valid config_id
            if agent_info['config_id']:
                hardcoded_agents.append({
                    'id': agent_id,
                    'name': agent_info['name'],
                    'voice': agent_info['voice'],
                    'model': agent_info['model'],
                    'specialty': agent_info['specialty'],
                    'description': agent_info['description']
                })
        
        return JsonResponse({
            'success': True,
            'database_agents': {
                'count': len(db_agents),
                'agents': db_agents,
                'usage': 'Use numeric id (1, 2, 3...) in API calls'
            },
            'hardcoded_agents': {
                'count': len(hardcoded_agents),
                'agents': hardcoded_agents,
                'usage': 'Use string id ("sarah_sales", etc.) in API calls'
            },
            'total_count': len(db_agents) + len(hardcoded_agents)
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 2: INITIATE CALL
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def initiate_call(request):
    try:
        # Parse request body
        logger.info(f"📥 Received request body: {request.body.decode('utf-8')}")
        data = json.loads(request.body)
        logger.info(f"📊 Parsed data: {data}")
        
        # Parse incoming parameters
        # Support new keys: configId (preferred) and phone_no
        # Keep backward compatibility with phone_number/customer_phone and agent_id
        phone_number = data.get('phone_no') or data.get('phone_number') or data.get('customer_phone')
        agent_id = data.get('agent_id')
        requested_config_id = data.get('configId') or data.get('config_id')

        logger.info(f"🔍 Validating: phone_number={phone_number}, agent_id={agent_id}, configId={requested_config_id}")

        # phone_number is required
        if not phone_number:
            logger.warning(f"❌ Missing phone number. Data received: {data}")
            return JsonResponse({
                'success': False,
                'error': 'phone_no (or phone_number/customer_phone) is required',
                'received_data': data
            }, status=400)
        
        # Prepare agent lookup
        db_agent = None
        agent_info = None

        # If a specific Hume config is requested, build a minimal agent_info
        if requested_config_id:
            logger.info(f"🔧 Using explicit configId from request: {requested_config_id}")
            # Create minimal agent_info using requested config
            agent_info = {
                'name': f'CustomConfig-{requested_config_id[:8]}',
                'config_id': requested_config_id,
                'voice': 'default',
                'model': 'custom',
                'specialty': 'custom-config'
            }
            # We do not require agent_id when configId is provided
        else:
            try:
                # ✅ FIXED: Use Agent model from agents app (not HumeAgent)
                from agents.models import Agent

                # ✅ Check if any active OUTBOUND agents exist
                total_agents = Agent.objects.filter(
                    agent_type__in=['outbound', 'outbound_api', 'both'],
                    status='active'
                ).count()

                if total_agents == 0:
                    logger.error("❌ NO ACTIVE OUTBOUND AGENTS FOUND IN DATABASE")
                    return JsonResponse({
                        'success': False,
                        'error': 'No active outbound agents in database. Please create an outbound agent first.',
                        'hint': 'Use Agent model with agent_type=outbound'
                    }, status=404)

                # If no agent_id provided, use the default (first active outbound agent)
                if not agent_id:
                    db_agent = Agent.objects.filter(
                        agent_type__in=['outbound', 'outbound_api', 'both'],
                        status='active'
                    ).order_by('created_at').first()
                    logger.info(f"🔎 No agent_id provided - using default outbound agent: {db_agent.name}")

                else:
                    agent_id_str = str(agent_id)

                    # Case 1: Numeric index provided (1-based index) - LEGACY SUPPORT
                    if agent_id_str.isdigit():
                        logger.info(f"🔢 Numeric agent_id provided: {agent_id_str}, fetching by index...")
                        # Get all active outbound agents and pick by index
                        all_agents = Agent.objects.filter(
                            agent_type__in=['outbound', 'outbound_api', 'both'],
                            status='active'
                        ).order_by('created_at')
                        agent_index = int(agent_id_str) - 1  # Convert to 0-based index
                        
                        # ✅ Proper validation
                        if agent_index >= 0 and agent_index < all_agents.count():
                            db_agent = all_agents[agent_index]
                            logger.info(f"✅ Found agent at index {agent_id_str}: {db_agent.name}")
                        else:
                            logger.error(f"❌ Agent index {agent_id_str} out of range (valid: 1-{total_agents})")
                            return JsonResponse({
                                'success': False,
                                'error': f'Agent index {agent_id_str} out of range',
                                'available_indices': f'1-{total_agents}',
                                'total_active_agents': total_agents
                            }, status=400)
                    
                    # Case 2: UUID string provided (PRIMARY - from frontend dropdown)
                    else:
                        logger.info(f"🆔 UUID provided: {agent_id_str}, fetching Agent from database...")
                        # ✅ FIXED: Query Agent model with outbound filter
                        db_agent = Agent.objects.filter(
                            id=agent_id_str,
                            agent_type__in=['outbound', 'outbound_api', 'both'],
                            status='active'
                        ).first()
                        
                        if db_agent:
                            logger.info(f"✅ Found Agent by UUID: {db_agent.name} (ID: {db_agent.id})")
                        else:
                            # Better error with available agents list
                            available_agents = Agent.objects.filter(
                                agent_type__in=['outbound', 'outbound_api', 'both'],
                                status='active'
                            ).order_by('created_at')[:5]
                            
                            agent_list = [
                                f"• {agent.name} (ID: {agent.id})" 
                                for agent in available_agents
                            ]
                            
                            logger.error(f"❌ Agent UUID not found: {agent_id_str}")
                            return JsonResponse({
                                'success': False,
                                'error': f'Agent with ID {agent_id_str} not found or not an outbound agent',
                                'hint': 'Make sure agent exists, is active, and agent_type is outbound/outbound_api/both',
                                'available_outbound_agents': agent_list,
                                'total_outbound_agents': total_agents
                            }, status=404)
                
                # If found in database, use it
                if db_agent:
                    # Check if agent has HumeAI config
                    if not db_agent.hume_config_id:
                        logger.error(f"❌ Agent {db_agent.name} has no hume_config_id")
                        return JsonResponse({
                            'success': False,
                            'error': f'Agent "{db_agent.name}" does not have HumeAI config_id configured. Please sync the agent first.',
                            'agent_id': str(db_agent.id),
                            'agent_name': db_agent.name
                        }, status=400)
                    
                    # ✅ Use Agent model configuration (not HumeAgent)
                    # Map voice_model to HumeAI voice names
                    voice_mapping = {
                        'en-US-female-1': 'ITO',
                        'en-US-male-1': 'DACHER',
                        'en-US-female-2': 'KORA',
                        'en-US-male-2': 'FINN',
                    }
                    voice_name = voice_mapping.get(db_agent.voice_model, 'ITO')
                    
                    agent_info = {
                        'name': db_agent.name,
                        'config_id': db_agent.hume_config_id,
                        'voice': voice_name,  # ✅ Mapped from voice_model
                        'model': 'Claude 3.5 Sonnet',
                        'specialty': db_agent.voice_tone or 'Professional Assistant',  # ✅ Changed from description
                        'description': getattr(db_agent, 'sales_script_text', '') or f"{db_agent.name} - Outbound Agent"  # ✅ Changed from system_prompt
                    }
                    agent_id = str(db_agent.id)  # Use actual UUID for tracking
                    logger.info(f"✅ Agent lookup complete: {db_agent.name} (config: {db_agent.hume_config_id})")
        
            except Exception as db_error:
                logger.error(f"❌ Database error during agent lookup: {db_error}")
                import traceback
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'success': False,
                    'error': f'Database error: {str(db_error)}'
                }, status=500)
        
        # If no DB agent found, check AVAILABLE_AGENTS (hardcoded agents - legacy)
        if not db_agent and agent_id and agent_info is None:
            agent_id_str = str(agent_id)
            if agent_id_str in AVAILABLE_AGENTS:
                agent_info = AVAILABLE_AGENTS[agent_id_str]
                agent_id = agent_id_str
                logger.info(f"✅ Using hardcoded agent: {agent_info['name']}")
            else:
                # ✅ Better error message with available agents from Agent model
                try:
                    from agents.models import Agent
                    db_agents = Agent.objects.filter(
                        agent_type__in=['outbound', 'outbound_api', 'both'],
                        status='active'
                    ).order_by('created_at')[:5]
                    agent_list = [f"{idx+1}. {agent.name} (ID: {agent.id})" for idx, agent in enumerate(db_agents)]
                except:
                    agent_list = []
                
                logger.error(f"❌ Agent not found: {agent_id_str}")
                return JsonResponse({
                    'success': False,
                    'error': 'Agent not found',
                    'available_agents': {
                        'database_agents': agent_list if agent_list else "No active outbound agents",
                        'hardcoded_agents': list(AVAILABLE_AGENTS.keys())
                    },
                    'hint': 'Use UUID from dropdown or numeric ID (1, 2, 3...) for database agents'
                }, status=404)
        
        # ✅ FIX 2: Validate we have a config id from either agent_info or explicit request
        final_config_id = None
        if agent_info and agent_info.get('config_id'):
            final_config_id = agent_info.get('config_id')

        if not final_config_id:
            logger.error("❌ No HumeAI config_id available")
            return JsonResponse({
                'success': False,
                'error': 'No HumeAI config_id available. Provide configId in request or select a configured agent.'
            }, status=400)

        # Optional fields
        customer_name = data.get('customer_name') or data.get('name') or 'Customer'
        customer_email = data.get('email') or data.get('customer_email')
        metadata = data.get('metadata', {}) or {}

        # Attach config id and optional email to metadata
        metadata['config_id'] = final_config_id
        if customer_email:
            metadata['customer_email'] = customer_email

        # Validate phone number format
        if not phone_number.startswith('+'):
            return JsonResponse({
                'success': False,
                'error': 'phone_number must include country code (e.g., +1234567890)'
            }, status=400)
        
        logger.info(f"📞 Initiating call to {phone_number} with agent {agent_id}")
        logger.info(f"🔊 Using voice provider: {VOICE_PROVIDER}")
        
        # ✅ FIX 1: UNIFIED CALL INITIATION - Works for both providers
        call = None
        call_sid = None
        
        try:
            if VOICE_PROVIDER == 'vonage':
                # Initiate Vonage call
                if not vonage_client:
                    return JsonResponse({
                        'success': False,
                        'error': 'Vonage client not initialized. Check VONAGE_API_KEY and VONAGE_API_SECRET in settings.'
                    }, status=500)
                
                logger.info(f"📞 Initiating Vonage call...")
                
                # ✅ FIXED: Pass as dictionary to create_call, strip '+' from phone numbers
                to_clean = phone_number.lstrip('+')
                from_clean = VONAGE_PHONE_NUMBER.lstrip('+')
                
                call = vonage_client.voice.create_call({
                    "to": [{"type": "phone", "number": to_clean}],
                    "from_": {"type": "phone", "number": from_clean},
                    "answer_url": [f"{BASE_URL}/api/hume-twilio/vonage-outgoing-answer/"],
                    "event_url": [f"{BASE_URL}/api/hume-twilio/vonage-event-callback/"]
                })
                
                # Vonage SDK returns CreateCallResponse object (not dict)
                # Access properties directly, not with .get()
                call_sid = call.uuid if hasattr(call, 'uuid') else str(call)
                logger.info(f"✅ Vonage call initiated: {call_sid}")
                
            else:  # Default to Twilio
                # Initiate Twilio call
                if not twilio_client:
                    return JsonResponse({
                        'success': False,
                        'error': 'Twilio client not initialized. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in settings.'
                    }, status=500)
                
                logger.info(f"📞 Initiating Twilio call...")
                
                call = twilio_client.calls.create(
                    to=phone_number,
                    from_=TWILIO_PHONE_NUMBER,
                    url=f"{BASE_URL}/api/hume-twilio/voice-webhook-fixed/",
                    status_callback=f"{BASE_URL}/api/hume-twilio/status-callback-fixed/",
                    status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                    status_callback_method='POST',
                    record=False,
                    timeout=60
                )
                
                call_sid = call.sid
                logger.info(f"✅ Twilio call initiated: {call_sid}")
                
        except Exception as provider_error:
            logger.error(f"❌ Call initiation failed: {provider_error}")
            return JsonResponse({
                'success': False,
                'error': f'{VOICE_PROVIDER.upper()} call initiation failed: {str(provider_error)}',
                'provider': VOICE_PROVIDER
            }, status=500)
        
        # ✅ FIX 1: UNIFIED DATABASE SAVE - Works for BOTH Vonage and Twilio
        try:
            from HumeAiTwilio.models import TwilioCall
            
            # Prepare call data (WITHOUT agent ForeignKey - TwilioCall.agent expects HumeAgent)
            call_data = {
                'call_sid': call_sid,
                'to_number': phone_number,
                'from_number': VONAGE_PHONE_NUMBER if VOICE_PROVIDER == 'vonage' else TWILIO_PHONE_NUMBER,
                'status': 'initiated',  # ✅ Better than 'queued'
                'direction': 'outbound_api',
                'customer_name': customer_name,
                'customer_email': customer_email,
                'provider': VOICE_PROVIDER,  # ✅ Tracks provider
                'hume_config_id': final_config_id  # ✅ Store config ID
            }
            
            # ✅ FIXED: Store agent info in metadata (not as ForeignKey)
            # TwilioCall.agent expects HumeAgent, but we're using Agent model
            if db_agent:
                # Store agent details in metadata JSON field (if available)
                metadata['agent_id'] = str(db_agent.id)
                metadata['agent_name'] = db_agent.name
                metadata['agent_type'] = db_agent.agent_type
                logger.info(f"✅ Storing agent in metadata: {db_agent.name}")
            
            # Add metadata to call_data if TwilioCall has metadata field
            if hasattr(TwilioCall, 'metadata'):
                call_data['metadata'] = json.dumps(metadata)
            
            # Create call record
            db_call = TwilioCall.objects.create(**call_data)
            
            logger.info(f"💾 ✅ Call saved to database: {db_call.id}")
            logger.info(f"📱 Provider: {db_call.provider}, Agent: {db_agent.name if db_agent else 'None'}")
            
        except Exception as db_error:
            logger.error(f"❌ Database save failed: {db_error}")
            import traceback
            logger.error(traceback.format_exc())
        
        # ✅ PROVIDER-SPECIFIC RETURN - Returns raw provider data
        # Build common response structure
        response_data = {
            'success': True,
            'message': f'✅ Call initiated successfully via {VOICE_PROVIDER.upper()}',
            'provider': VOICE_PROVIDER,
            'agent': {
                'id': agent_id,
                'name': agent_info['name'] if agent_info else None,
                'config_id': final_config_id,
                'specialty': agent_info.get('specialty') if agent_info else None,
                'voice': agent_info.get('voice') if agent_info else None,
                'model': agent_info.get('model') if agent_info else None
            },
            'customer': {
                'phone': phone_number,
                'name': customer_name,
                'email': customer_email
            },
            'metadata': metadata,
            'initiated_at': datetime.now().isoformat()
        }
        
        # Add provider-specific call data
        if VOICE_PROVIDER == 'vonage':
            # Return Vonage-specific response format
            # Vonage SDK returns CreateCallResponse object with properties
            response_data['call'] = {
                'uuid': getattr(call, 'uuid', call_sid),
                'status': getattr(call, 'status', 'started'),
                'direction': getattr(call, 'direction', 'outbound'),
                'conversation_uuid': getattr(call, 'conversation_uuid', None),
                'timestamp': getattr(call, 'timestamp', None),
                # Full Vonage response for debugging (convert to dict if possible)
                '_provider_response': {
                    'uuid': getattr(call, 'uuid', None),
                    'status': getattr(call, 'status', None),
                    'direction': getattr(call, 'direction', None),
                    'conversation_uuid': getattr(call, 'conversation_uuid', None)
                }
            }
            logger.info(f"📤 Returning Vonage call data: UUID={call_sid}")
        else:
            # Return Twilio-specific response format
            response_data['call'] = {
                'sid': call.sid,  # Twilio call SID
                'status': call.status,
                'direction': call.direction,
                'from': call.from_,
                'to': call.to,
                'date_created': call.date_created.isoformat() if call.date_created else None,
                'price': call.price,
                'price_unit': call.price_unit,
                # Full Twilio response for debugging
                '_provider_response': {
                    'account_sid': call.account_sid,
                    'api_version': call.api_version,
                    'answered_by': call.answered_by,
                    'caller_name': call.caller_name,
                    'duration': call.duration,
                    'end_time': call.end_time.isoformat() if call.end_time else None,
                    'start_time': call.start_time.isoformat() if call.start_time else None
                }
            }
            logger.info(f"📤 Returning Twilio call data: SID={call.sid}")
        
        return JsonResponse(response_data, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        logger.error(f"❌ Error initiating call: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 3: GET CALL STATUS
# ═══════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def get_call_status(request, call_sid):
    """
    Get quick call status (lightweight) - Database-first with provider fallback
    
    GET /api/hume-twilio/call-status/{call_sid}/
    
    Strategy:
    1. 🥇 PRIMARY: Get from local database (fast, free)
    2. 🥈 FALLBACK: If not in DB, fetch from provider API
    
    For complete conversation data, use /get-call-data/{call_sid}/
    """
    try:
        # 🥇 STEP 1: Try to get from DATABASE first (PRIMARY SOURCE)
        try:
            from HumeAiTwilio.models import TwilioCall
            db_call = TwilioCall.objects.filter(call_sid=call_sid).first()
            
            metadata = {}
            provider = VOICE_PROVIDER  # Default to settings
            
            if db_call:
                logger.info(f"✅ Found call in DATABASE: {call_sid}")
                provider = db_call.provider or VOICE_PROVIDER
                
                # Extract metadata
                if db_call.metadata:
                    try:
                        metadata = json.loads(db_call.metadata) if isinstance(db_call.metadata, str) else db_call.metadata
                    except:
                        pass
                
                # 🎯 Return database data directly (no API call needed!)
                call_data = {
                    'call_sid': db_call.call_sid,
                    'status': db_call.status,
                    'duration': db_call.duration or 0,
                    'from': db_call.from_number,
                    'to': db_call.to_number,
                    'direction': db_call.direction,
                    'start_time': db_call.started_at.isoformat() if db_call.started_at else None,
                    'end_time': db_call.ended_at.isoformat() if db_call.ended_at else None,
                    'created_at': db_call.created_at.isoformat() if db_call.created_at else None,
                    '_data_source': 'database'
                }
                
                logger.info(f"📊 Returning database data: status={db_call.status}, duration={db_call.duration}s")
                
                return JsonResponse({
                    'success': True,
                    'provider': provider,
                    'call': call_data,
                    'agent': {
                        'id': metadata.get('agent_id'),
                        'name': metadata.get('agent_name')
                    },
                    'customer': {
                        'name': metadata.get('customer_name'),
                        'email': metadata.get('customer_email')
                    },
                    'metadata': metadata,
                    'data_source': 'database'
                }, status=200)
                
        except Exception as db_error:
            logger.warning(f"⚠️ Database lookup failed: {db_error}")
            db_call = None
            metadata = {}
            provider = VOICE_PROVIDER
        
        # 🥈 STEP 2: If not in database, fetch from PROVIDER API (FALLBACK)
        logger.warning(f"⚠️ Call not found in database, fetching from {provider.upper()} API...")
        
        call_data = {}
        if provider == 'vonage':
            # Vonage call fetch - SDK returns object, not dict
            call = vonage_client.voice.get_call(call_sid)
            
            # Handle both dict and object responses
            def get_value(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)
            
            call_data = {
                'call_sid': get_value(call, 'uuid', call_sid),
                'status': get_value(call, 'status', 'unknown'),
                'duration': get_value(call, 'duration', 0),
                'from': get_value(get_value(call, 'from', {}), 'number') if isinstance(get_value(call, 'from'), dict) else get_value(call, 'from'),
                'to': get_value(get_value(call, 'to', {}), 'number') if isinstance(get_value(call, 'to'), dict) else get_value(call, 'to'),
                'direction': get_value(call, 'direction', 'outbound'),
                'start_time': get_value(call, 'start_time'),
                'end_time': get_value(call, 'end_time'),
                'conversation_uuid': get_value(call, 'conversation_uuid'),
                'network': get_value(call, 'network'),
                '_data_source': 'vonage_api',
                '_provider_response': call if isinstance(call, dict) else str(call)
            }
            logger.info(f"✅ Fetched from Vonage API: {call_data['status']}")
        else:
            # Twilio call fetch
            call = twilio_client.calls(call_sid).fetch()
            call_data = {
                'call_sid': call.sid,
                'status': call.status,
                'duration': call.duration or 0,
                'from': call.from_,
                'to': call.to,
                'direction': call.direction,
                'start_time': call.start_time.isoformat() if call.start_time else None,
                'end_time': call.end_time.isoformat() if call.end_time else None,
                'price': call.price,
                'price_unit': call.price_unit,
                '_data_source': 'twilio_api',
                '_provider_response': {
                    'account_sid': call.account_sid,
                    'answered_by': call.answered_by
                }
            }
            logger.info(f"✅ Fetched from Twilio API: {call.status}")
        
        return JsonResponse({
            'success': True,
            'provider': provider,
            'call': call_data,
            'agent': {
                'id': metadata.get('agent_id'),
                'name': metadata.get('agent_name')
            },
            'customer': {
                'name': metadata.get('customer_name'),
                'email': metadata.get('customer_email')
            },
            'metadata': metadata,
            'data_source': f'{provider}_api'  # Indicates API was used
        }, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error getting call status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 3B: GET COMPLETE CALL DATA (NEW - COMPREHENSIVE)
# ═══════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def get_call_data(request, call_sid):
    """
    🔥 Get COMPLETE call data with conversation, emotions, and analytics
    
    GET /api/hume-twilio/get-call-data/{call_sid}/
    
    Returns:
    - Call metadata (status, duration, price)
    - Complete conversation logs (all messages with timestamps)
    - Separate customer & agent transcripts
    - HumeAI emotion analysis for each message
    - Customer sentiment analytics
    - Engagement metrics
    
    Use this API to get full conversation details after call completes
    """
    try:
        logger.info(f"📊 Fetching complete call data for: {call_sid}")
        
        # Get from database with related data (PRIMARY SOURCE - Fast & Free!)
        db_call = None
        metadata = {}
        conversation_logs = []
        customer_messages = []
        agent_messages = []
        emotions = []
        call_data = None
        
        try:
            from HumeAiTwilio.models import TwilioCall, ConversationLog
            
            db_call = TwilioCall.objects.filter(call_sid=call_sid).first()
            
            if not db_call:
                logger.warning(f"⚠️ Call not found in database: {call_sid}")
                return JsonResponse({
                    'success': False,
                    'error': 'Call not found in database. Please use a valid call_sid from an actual call.',
                    'hint': 'First initiate a call using /initiate-call/ API, then use the returned call_sid here.'
                }, status=404)
            
            # ✅ PRIMARY: Use database data (fast & free)
            call_data = {
                'call_sid': db_call.call_sid,
                'status': db_call.status or 'unknown',
                'duration': db_call.duration or 0,
                'from': db_call.from_number,
                'to': db_call.to_number,
                'direction': db_call.direction or 'outbound',
                'start_time': db_call.started_at.isoformat() if db_call.started_at else None,
                'end_time': db_call.ended_at.isoformat() if db_call.ended_at else None,
                'price': None,  # Twilio only
                'price_unit': None  # Twilio only
            }
            logger.info(f"✅ Using database call data: {db_call.status}")
            
            # Parse metadata (TwilioCall model may not have metadata field)
            if hasattr(db_call, 'metadata') and db_call.metadata:
                try:
                    metadata = json.loads(db_call.metadata) if isinstance(db_call.metadata, str) else db_call.metadata
                except:
                    metadata = {}
            else:
                # Build metadata from available fields
                metadata = {
                    'agent_id': str(db_call.agent.id) if db_call.agent else None,
                    'agent_name': db_call.agent.name if db_call.agent else None,
                    'config_id': db_call.agent.hume_config_id if db_call.agent else None,
                    'customer_name': db_call.customer_name,
                    'customer_email': db_call.customer_email
                }
            
            # Get conversation logs
            logs = ConversationLog.objects.filter(call=db_call).order_by('timestamp')
            
            logger.info(f"📝 Found {logs.count()} conversation logs")
            
            for log in logs:
                # Map role to speaker label
                speaker = 'customer' if log.role == 'user' else 'agent' if log.role == 'assistant' else log.role
                
                log_entry = {
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                    'role': log.role,
                    'speaker': speaker,
                    'message': log.message,
                    'sentiment': log.sentiment,
                    'confidence': log.confidence
                }
                
                conversation_logs.append(log_entry)
                
                # Separate customer and agent messages
                if log.role in ['user']:
                    customer_messages.append({
                        'message': log.message,
                        'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                        'sentiment': log.sentiment,
                        'confidence': log.confidence
                    })
                elif log.role in ['assistant']:
                    agent_messages.append({
                        'message': log.message,
                        'timestamp': log.timestamp.isoformat() if log.timestamp else None
                    })
                
                # Extract emotions if available
                if hasattr(log, 'emotion_scores') and log.emotion_scores:
                    try:
                        emotion_data = json.loads(log.emotion_scores) if isinstance(log.emotion_scores, str) else log.emotion_scores
                        if emotion_data:
                            emotions.append({
                                'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                                'role': log.role,
                                'speaker': speaker,
                                'emotions': emotion_data
                            })
                    except Exception as emotion_error:
                        logger.warning(f"⚠️ Could not parse emotions: {emotion_error}")
        
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}")
            import traceback
            logger.error(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': f'Database error: {str(db_error)}'
            }, status=500)
        
        # ✅ SECONDARY: Try to get price info from provider (optional, only if needed)
        try:
            if call_data and call_data.get('status') == 'completed':
                provider = db_call.provider if db_call else VOICE_PROVIDER
                logger.info(f"💰 Fetching price info from {provider.upper()}...")
                
                if provider == 'vonage':
                    # Vonage pricing fetch - SDK returns object, not dict
                    try:
                        call = vonage_client.voice.get_call(call_sid)
                        
                        # Helper to get value from object or dict
                        def get_value(obj, key, default=None):
                            if isinstance(obj, dict):
                                return obj.get(key, default)
                            return getattr(obj, key, default)
                        
                        call_data['price'] = get_value(call, 'price')
                        call_data['rate'] = get_value(call, 'rate')
                        call_data['network'] = get_value(call, 'network')
                        logger.info(f"✅ Updated with Vonage price: {call_data.get('price')}")
                    except Exception as vonage_error:
                        logger.warning(f"⚠️ Could not fetch price from Vonage (optional): {vonage_error}")
                else:
                    # Twilio pricing fetch
                    call = twilio_client.calls(call_sid).fetch()
                    call_data['price'] = call.price
                    call_data['price_unit'] = call.price_unit
                    logger.info(f"✅ Updated with Twilio price: {call.price} {call.price_unit}")
        except Exception as provider_error:
            logger.warning(f"⚠️ Could not fetch price from provider (optional): {provider_error}")
            # Not critical - continue without price info
        
        # Calculate analytics
        total_messages = len(conversation_logs)
        customer_message_count = len(customer_messages)
        agent_message_count = len(agent_messages)
        
        # Average sentiment
        sentiments = [msg.get('sentiment', 0) for msg in customer_messages if msg.get('sentiment') is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Sentiment distribution
        positive_count = sum(1 for s in sentiments if s > 0.3)
        negative_count = sum(1 for s in sentiments if s < -0.3)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        # Direction indicator (handle all outbound variations)
        direction = call_data.get('direction', 'outbound')
        is_outbound = direction in ['outbound', 'outbound_api', 'outbound-api']
        direction_badge = "📞 Outbound" if is_outbound else "📱 Inbound"
        
        # Data source tracking
        data_sources_used = {
            'call_metadata': 'database',
            'conversation': 'database',
            'emotions': 'database',
            'price_info': 'twilio' if call_data.get('price') else 'not_available'
        }
        
        # Construct comprehensive response
        response_data = {
            'success': True,
            'call': {
                **call_data,
                'direction_badge': direction_badge
            },
            'agent': {
                'id': metadata.get('agent_id'),
                'name': metadata.get('agent_name'),
                'config_id': metadata.get('config_id')
            },
            'customer': {
                'name': metadata.get('customer_name'),
                'email': metadata.get('customer_email'),
                'phone': call_data.get('to')
            },
            'conversation': {
                'total_messages': total_messages,
                'customer_messages': customer_message_count,
                'agent_messages': agent_message_count,
                'full_logs': conversation_logs,
                'customer_transcript': customer_messages,
                'agent_transcript': agent_messages
            },
            'transcript': {
                'formatted': _format_transcript(conversation_logs),
                'plain_text': _generate_plain_transcript(conversation_logs),
                'total_exchanges': total_messages // 2,  # Rough estimate
                'data_source': 'database'
            },
            'emotions': {
                'count': len(emotions),
                'data': emotions,
                'has_emotion_data': len(emotions) > 0
            },
            'analytics': {
                'sentiment': {
                    'average': round(avg_sentiment, 3),
                    'label': 'positive' if avg_sentiment > 0.3 else 'negative' if avg_sentiment < -0.3 else 'neutral',
                    'distribution': {
                        'positive': positive_count,
                        'neutral': neutral_count,
                        'negative': negative_count
                    }
                },
                'engagement': {
                    'score': min(100, (total_messages * 10)),
                    'total_interactions': total_messages,
                    'avg_message_length': sum(len(msg['message']) for msg in customer_messages) / customer_message_count if customer_message_count > 0 else 0
                }
            },
            'metadata': metadata,
            'data_sources': data_sources_used
        }
        
        logger.info(f"✅ Successfully fetched call data: {total_messages} messages, {len(emotions)} emotion data points")
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error getting call data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 4: BULK CALL INITIATION
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def initiate_bulk_calls(request):
    """
    Initiate multiple calls at once
    
    POST /api/call/initiate-bulk/
    
    Body:
    {
        "agent_id": "sarah_sales",
        "calls": [
            {
                "phone_number": "+1234567890",
                "customer_name": "John Doe"
            },
            {
                "phone_number": "+0987654321",
                "customer_name": "Jane Smith"
            }
        ],
        "metadata": {
            "campaign": "Q4 Outreach"
        }
    }
    
    Response:
    {
        "success": true,
        "total": 2,
        "initiated": 2,
        "failed": 0,
        "calls": [...]
    }
    """
    try:
        data = json.loads(request.body)
        
        agent_id = data.get('agent_id')
        calls_data = data.get('calls', [])
        metadata = data.get('metadata', {})
        
        if not agent_id or not calls_data:
            return JsonResponse({
                'success': False,
                'error': 'agent_id and calls array required'
            }, status=400)
        
        results = []
        initiated_count = 0
        failed_count = 0
        
        for call_data in calls_data:
            phone_number = call_data.get('phone_number')
            customer_name = call_data.get('customer_name', 'Customer')
            
            try:
                # Create individual call request
                call_request = {
                    'phone_number': phone_number,
                    'agent_id': agent_id,
                    'customer_name': customer_name,
                    'metadata': metadata
                }
                
                # Simulate request object
                from django.http import HttpRequest
                req = HttpRequest()
                req.body = json.dumps(call_request).encode()
                req.method = 'POST'
                
                # Call initiate_call function
                response = initiate_call(req)
                response_data = json.loads(response.content)
                
                if response_data.get('success'):
                    initiated_count += 1
                    results.append({
                        'phone_number': phone_number,
                        'status': 'initiated',
                        'call_sid': response_data['call']['call_sid']
                    })
                else:
                    failed_count += 1
                    results.append({
                        'phone_number': phone_number,
                        'status': 'failed',
                        'error': response_data.get('error')
                    })
                    
            except Exception as e:
                failed_count += 1
                results.append({
                    'phone_number': phone_number,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'message': f'Bulk call initiation completed',
            'total': len(calls_data),
            'initiated': initiated_count,
            'failed': failed_count,
            'calls': results
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 5: GET ALL RECENT CALLS (NEW)
# ═══════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def get_all_calls(request):
    """
    🔥 Get all recent calls with complete data
    
    GET /api/hume-twilio/get-all-calls/?limit=20
    
    Query Params:
    - limit: Number of calls to return (default: 20, max: 100)
    - status: Filter by status (initiated, completed, failed, etc.)
    
    Returns list of calls with:
    - Call metadata
    - Direction indicator (inbound/outbound)
    - Data source (database/twilio)
    - Agent & customer info
    """
    try:
        # Get query params
        limit = int(request.GET.get('limit', 20))
        limit = min(limit, 100)  # Max 100 calls
        status_filter = request.GET.get('status')
        
        logger.info(f"📊 Fetching recent calls (limit={limit}, status={status_filter})")
        
        from HumeAiTwilio.models import TwilioCall
        
        # Query database
        query = TwilioCall.objects.all()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        calls = query.order_by('-created_at')[:limit]
        
        # Build response
        call_list = []
        for call in calls:
            # Direction indicator (handle all outbound variations)
            is_outbound = call.direction in ['outbound', 'outbound_api', 'outbound-api']
            direction_badge = "📞 Outbound" if is_outbound else "📱 Inbound"
            
            # Build metadata
            if hasattr(call, 'metadata') and call.metadata:
                try:
                    metadata = json.loads(call.metadata) if isinstance(call.metadata, str) else call.metadata
                except:
                    metadata = {}
            else:
                metadata = {
                    'agent_id': str(call.agent.id) if call.agent else None,
                    'agent_name': call.agent.name if call.agent else None,
                    'config_id': call.agent.hume_config_id if call.agent else None,
                    'customer_name': call.customer_name,
                    'customer_email': call.customer_email
                }
            
            # Get transcript preview (first 3 messages)
            from HumeAiTwilio.models import ConversationLog
            conversation_logs = ConversationLog.objects.filter(
                call=call  # ForeignKey relationship, not call_sid
            ).order_by('timestamp')[:3]
            
            transcript_preview = []
            for log in conversation_logs:
                transcript_preview.append({
                    'role': log.role,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None
                })
            
            # Count total messages
            total_messages = ConversationLog.objects.filter(call=call).count()
            
            call_data = {
                'call_sid': call.call_sid,
                'status': call.status,
                'direction': call.direction,
                'direction_badge': direction_badge,
                'from': call.from_number,
                'to': call.to_number,
                'duration': call.duration or 0,
                'start_time': call.started_at.isoformat() if call.started_at else None,
                'end_time': call.ended_at.isoformat() if call.ended_at else None,
                'created_at': call.created_at.isoformat() if call.created_at else None,
                'agent': {
                    'id': metadata.get('agent_id'),
                    'name': metadata.get('agent_name'),
                    'config_id': metadata.get('config_id')
                },
                'customer': {
                    'name': metadata.get('customer_name') or call.customer_name,
                    'email': metadata.get('customer_email') or call.customer_email,
                    'phone': call.to_number
                },
                'transcript': {
                    'preview': transcript_preview,
                    'total_messages': total_messages,
                    'has_more': total_messages > 3
                },
                'data_source': 'database'  # Always from database for this API
            }
            
            call_list.append(call_data)
        
        logger.info(f"✅ Returning {len(call_list)} calls")
        
        return JsonResponse({
            'success': True,
            'total': len(call_list),
            'limit': limit,
            'calls': call_list,
            'data_source': 'database'
        }, status=200)
        
    except Exception as e:
        logger.error(f"❌ Error fetching calls: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
