"""
VOICE PROVIDER CSRF MIDDLEWARE BYPASS - Supports Twilio + Vonage
Custom middleware to bypass CSRF for voice provider webhooks
"""

from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class TwilioCsrfExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt Twilio & Vonage webhook URLs from CSRF verification
    MUST BE PLACED BEFORE django.middleware.csrf.CsrfViewMiddleware in MIDDLEWARE
    """
    
    def process_request(self, request):
        """
        Exempt voice provider webhook paths from CSRF
        Supports: Twilio, Vonage
        """
        # Twilio webhook paths
        twilio_paths = [
            '/api/calls/voice-response/',
            '/api/calls/call-status/', 
            '/api/calls/fallback/',
            '/api/calls/ultimate-production-webhook/',
            '/api/calls/enhanced-voice-webhook/',
            '/api/calls/pure-hume-webhook/',
            '/api/calls/hume-webhook/',
            '/api/calls/auto-voice-webhook/',
            '/api/hume-twilio/voice-webhook/',
            '/api/hume-twilio/status-callback/',
            '/api/hume-twilio/voice-webhook-fixed/',
            '/api/hume-twilio/status-callback-fixed/',
            '/api/hume-twilio/health/',
        ]
        
        # Vonage webhook paths
        vonage_paths = [
            '/api/hume-twilio/vonage-voice-webhook/',
            '/api/hume-twilio/vonage-event-callback/',
            '/api/hume-twilio/vonage-stream-callback/',
            '/api/hume-twilio/vonage-health/',
        ]
        
        # Combined paths
        exempt_paths = twilio_paths + vonage_paths
        
        # Check if this is a voice provider webhook request
        if request.path in exempt_paths:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            remote_addr = request.META.get('REMOTE_ADDR', '')
            forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            
            # Determine provider
            provider = 'unknown'
            if any(p in request.path for p in vonage_paths):
                provider = 'vonage'
                logger.info(f"📞 Vonage webhook detected: {request.path}")
            else:
                provider = 'twilio'
                logger.info(f"📞 Twilio webhook detected: {request.path}")
            
            logger.info(f"   Provider: {provider}")
            logger.info(f"   User-Agent: {user_agent}")
            logger.info(f"   Remote-Addr: {remote_addr}")
            logger.info(f"   X-Forwarded-For: {forwarded_for}")
            
            # Bypass CSRF for voice provider webhooks
            setattr(request, '_dont_enforce_csrf_checks', True)
            logger.info(f"   ✅ CSRF EXEMPTED for {provider} webhook")
            
            # Verify provider indicators
            is_voice_request = (
                'Twilio' in user_agent or 
                'Vonage' in user_agent or
                request.path in exempt_paths or
                remote_addr.startswith('54.') or  # Twilio IP
                remote_addr.startswith('52.') or  # Twilio IP
                remote_addr.startswith('5.') or   # Vonage IP
                'twilio' in forwarded_for.lower() if forwarded_for else False or
                'vonage' in forwarded_for.lower() if forwarded_for else False
            )
            
            if is_voice_request:
                logger.info(f"   🎯 CONFIRMED {provider} request indicators found")
            else:
                logger.warning(f"   ⚠️ Exempting path but {provider} indicators not found - might be test request")
        
        return None