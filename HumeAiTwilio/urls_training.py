"""
URLs for Agent Training APIs
"""
from django.urls import path
from HumeAiTwilio.api_views.agent_training import (
    train_from_call,
    train_from_document,
    train_from_sales_script,
    query_knowledge,
    get_training_stats,
    auto_train_webhook
)

urlpatterns = [
    # Train from call
    path('train-from-call/', train_from_call, name='train_from_call'),
    
    # Train from document (PDF/Word/TXT)
    path('train-from-document/', train_from_document, name='train_from_document'),
    
    # Train from sales script
    path('train-from-sales-script/', train_from_sales_script, name='train_from_sales_script'),
    
    # Query trained knowledge
    path('query-knowledge/', query_knowledge, name='query_knowledge'),
    
    # Get stats
    path('training-stats/', get_training_stats, name='training_stats'),
    
    # Auto-train webhook (called after each call)
    path('auto-train-webhook/', auto_train_webhook, name='auto_train_webhook'),
]
