"""
URLs for Call Initiation APIs
"""
from django.urls import path
from HumeAiTwilio.api_views.call_initiation import (
    get_available_agents,
    initiate_call,
    get_call_status,
    initiate_bulk_calls
)

urlpatterns = [
    # Get available agents
    path('agents/', get_available_agents, name='get_available_agents'),
    
    # Initiate single call
    path('initiate/', initiate_call, name='initiate_call'),
    
    # Get call status
    path('status/<str:call_sid>/', get_call_status, name='get_call_status'),
    
    # Bulk call initiation
    path('initiate-bulk/', initiate_bulk_calls, name='initiate_bulk_calls'),
]
