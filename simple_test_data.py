import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from calls.models import CallSession
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
user = User.objects.get(email='testvoice@admin.com')

# Create 10 test calls
for i in range(10):
    call_type = 'inbound' if i % 2 == 0 else 'outbound'
    CallSession.objects.create(
        user=user,
        call_type=call_type,
        caller_number=f'+1800COMPANY{i}' if call_type == 'inbound' else user.phone or '+1234567890',
        callee_number=f'+155566677{i}' if call_type == 'outbound' else user.phone or '+1234567890',
        status=['completed', 'answered', 'completed', 'answered'][i % 4],
        started_at=timezone.now() - timedelta(days=i),
        duration=60 + (i * 30),
        notes=f'Test call {i+1} - Sample conversation'
    )

print('Created 10 test calls')
print(f'Total: {CallSession.objects.filter(user=user).count()}')
print(f'Inbound: {CallSession.objects.filter(user=user, call_type="inbound").count()}')
print(f'Outbound: {CallSession.objects.filter(user=user, call_type="outbound").count()}')
