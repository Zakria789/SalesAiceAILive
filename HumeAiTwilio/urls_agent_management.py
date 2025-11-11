"""
HumeAI Agent Management URLs
"""
from django.urls import path
from HumeAiTwilio.views.agent_management import (
    create_agent,
    update_agent_prompt,
    list_agents,
    get_agent,
    delete_agent
)

urlpatterns = [
    # Create new agent (HumeAI + Local DB)
    path('agents/create/', create_agent, name='create_agent'),
    
    # Update existing agent prompt
    path('agents/update-prompt/', update_agent_prompt, name='update_agent_prompt'),
    
    # List all agents
    path('agents/list/', list_agents, name='list_agents'),
    
    # Get single agent
    path('agents/<str:config_id>/', get_agent, name='get_agent'),
    
    # Delete agent from local DB
    path('agents/<str:config_id>/delete/', delete_agent, name='delete_agent'),
]
