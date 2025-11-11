import os
import sys
import django
import json

# Ensure project root is on sys.path so Django settings module can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import TwilioCall, ConversationLog

def to_json(o):
    try:
        return str(o)
    except Exception:
        return None

# Get recent Vonage calls
recent_calls = list(TwilioCall.objects.filter(provider='vonage').order_by('-created_at').values(
    'call_sid','status','from_number','to_number','started_at','ended_at','duration','created_at'
)[:10])

print(json.dumps({'recent_calls': recent_calls}, default=to_json, indent=2))

# Inspect specific call from latest logs
call_sid = '1c156a5b-8c3a-4d02-acb3-f6dcb7702d88'
call = TwilioCall.objects.filter(call_sid=call_sid).first()
if call:
    logs_qs = ConversationLog.objects.filter(call=call).order_by('timestamp')
    logs = list(logs_qs.values('role','message','sentiment','confidence','timestamp')[:50])
    result = {
        'found_call': True,
        'call': {
            'id': str(call.id),
            'call_sid': call.call_sid,
            'status': call.status,
            'from_number': call.from_number,
            'to_number': call.to_number,
            'started_at': to_json(call.started_at),
            'ended_at': to_json(call.ended_at),
            'duration': call.duration
        },
        'log_count': logs_qs.count(),
        'logs_sample': logs
    }
else:
    result = {'found_call': False, 'call_sid': call_sid}

print(json.dumps(result, default=to_json, indent=2))
