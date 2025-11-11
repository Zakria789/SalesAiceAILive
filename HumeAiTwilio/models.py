from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class HumeAgent(models.Model):
    """HumeAI Agent Configuration"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    hume_config_id = models.CharField(max_length=255, help_text="HumeAI Configuration ID")
    
    # Agent Settings
    voice_name = models.CharField(max_length=100, default="ITO", help_text="Voice model name")
    language = models.CharField(max_length=10, default="en", help_text="Language code")
    
    # Personality & Behavior
    system_prompt = models.TextField(
        help_text="Instructions for the AI agent's behavior",
        default="You are a helpful sales assistant. Be friendly, professional, and helpful."
    )
    greeting_message = models.TextField(
        default="Hello! How can I help you today?",
        help_text="Initial greeting when call starts"
    )
    
    # 🔥 Sales Script & Knowledge Base
    sales_script_text = models.TextField(
        blank=True,
        null=True,
        help_text="Sales script text for the agent to follow during calls"
    )
    business_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Business information: company_name, website, industry, greeting, etc."
    )
    knowledge_files = models.JSONField(
        default=dict,
        blank=True,
        help_text="Knowledge base: product_catalog, pricing, features, FAQs, etc."
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='hume_agents')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hume_agents'
        ordering = ['-created_at']
        verbose_name = 'HumeAI Agent'
        verbose_name_plural = 'HumeAI Agents'
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class CustomerProfile(models.Model):
    """
    Customer Profile - Store customer information learned from calls
    Enables personalized experience on next calls
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Primary Identification
    phone_number = models.CharField(max_length=20, unique=True, db_index=True, help_text="Primary phone number")
    
    # Personal Information (learned from conversations)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    
    # Preferences & Context
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, blank=True, null=True)
    
    # Interaction History
    total_calls = models.IntegerField(default=0)
    last_call_date = models.DateTimeField(null=True, blank=True)
    
    # Customer Data (learned from conversations)
    learned_preferences = models.JSONField(blank=True, null=True, help_text="Any preferences mentioned by customer")
    previous_topics = models.JSONField(blank=True, null=True, help_text="Topics discussed in previous calls")
    custom_fields = models.JSONField(blank=True, null=True, help_text="Additional custom data learned")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hume_customer_profiles'  # Different table name to avoid conflict
        ordering = ['-last_call_date']
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['full_name']),
            models.Index(fields=['-last_call_date']),
        ]
    
    def __str__(self):
        name = self.full_name or 'Unknown'
        return f"{name} ({self.phone_number})"


class TwilioCall(models.Model):
    """Twilio Call Records with HumeAI Integration"""
    
    CALL_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('busy', 'Busy'),
        ('no_answer', 'No Answer'),
        ('canceled', 'Canceled'),
    ]
    
    CALL_DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    
    PROVIDER_CHOICES = [
        ('twilio', 'Twilio'),
        ('vonage', 'Vonage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Voice Provider Details
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='twilio', help_text="Voice service provider")
    call_sid = models.CharField(max_length=255, unique=True, help_text="Call ID from provider (Twilio SID or Vonage UUID)")
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    direction = models.CharField(max_length=20, choices=CALL_DIRECTION_CHOICES, default='outbound')
    status = models.CharField(max_length=20, choices=CALL_STATUS_CHOICES, default='initiated')
    
    # HumeAI Integration
    agent = models.ForeignKey(HumeAgent, on_delete=models.SET_NULL, null=True, related_name='calls')
    hume_config_id = models.CharField(max_length=255, blank=True, null=True, help_text="HumeAI Configuration ID used for this call")
    hume_session_id = models.CharField(max_length=255, blank=True, null=True)
    hume_chat_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Call Metadata
    duration = models.IntegerField(default=0, help_text="Call duration in seconds")
    recording_url = models.URLField(blank=True, null=True)
    
    # User Association
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='twilio_calls')
    customer_profile = models.ForeignKey('CustomerProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='calls', help_text="Linked customer profile")
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'twilio_calls'
        ordering = ['-created_at']
        verbose_name = 'Twilio Call'
        verbose_name_plural = 'Twilio Calls'
        indexes = [
            models.Index(fields=['call_sid']),
            models.Index(fields=['status']),
            models.Index(fields=['from_number']),
            models.Index(fields=['to_number']),
        ]
    
    def __str__(self):
        return f"{self.from_number} → {self.to_number} ({self.status})"


class ConversationLog(models.Model):
    """Store conversation messages between Customer and HumeAI Agent"""
    
    ROLE_CHOICES = [
        ('user', 'Customer'),
        ('assistant', 'AI Agent'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.ForeignKey(TwilioCall, on_delete=models.CASCADE, related_name='conversation_logs')
    
    # Message Details
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    
    # Emotion & Sentiment (from HumeAI)
    emotion_scores = models.JSONField(blank=True, null=True, help_text="Emotion detection scores")
    sentiment = models.CharField(max_length=20, blank=True, null=True)
    confidence = models.FloatField(default=0.0)
    
    # Metadata
    metadata = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'conversation_logs'
        ordering = ['timestamp']
        verbose_name = 'Conversation Log'
        verbose_name_plural = 'Conversation Logs'
    
    def __str__(self):
        return f"{self.role}: {self.message[:50]}..."


class CallAnalytics(models.Model):
    """Analytics and Insights from Calls"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(TwilioCall, on_delete=models.CASCADE, related_name='analytics')
    
    # Conversation Metrics
    total_messages = models.IntegerField(default=0)
    user_messages = models.IntegerField(default=0)
    agent_messages = models.IntegerField(default=0)
    
    # Sentiment Analysis
    overall_sentiment = models.CharField(max_length=20, blank=True, null=True)
    positive_score = models.FloatField(default=0.0)
    negative_score = models.FloatField(default=0.0)
    neutral_score = models.FloatField(default=0.0)
    
    # Emotion Analysis (Top emotions detected)
    top_emotions = models.JSONField(blank=True, null=True)
    
    # Call Quality
    interruptions = models.IntegerField(default=0)
    response_time_avg = models.FloatField(default=0.0, help_text="Average response time in seconds")
    
    # Business Metrics
    lead_qualified = models.BooleanField(default=False)
    appointment_booked = models.BooleanField(default=False)
    sale_made = models.BooleanField(default=False)
    
    # Additional Data
    keywords_mentioned = models.JSONField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'call_analytics'
        verbose_name = 'Call Analytics'
        verbose_name_plural = 'Call Analytics'
    
    def __str__(self):
        return f"Analytics for {self.call.call_sid}"


class WebhookLog(models.Model):
    """Log all webhook events from Twilio and HumeAI"""
    
    SOURCE_CHOICES = [
        ('twilio', 'Twilio'),
        ('hume', 'HumeAI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    event_type = models.CharField(max_length=100)
    
    # Webhook Data
    payload = models.JSONField()
    headers = models.JSONField(blank=True, null=True)
    
    # Processing Status
    processed = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)
    
    # Associations
    call = models.ForeignKey(TwilioCall, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhook_logs')
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhook_logs'
        ordering = ['-created_at']
        verbose_name = 'Webhook Log'
        verbose_name_plural = 'Webhook Logs'
        indexes = [
            models.Index(fields=['source', 'event_type']),
            models.Index(fields=['processed']),
        ]
    
    def __str__(self):
        return f"{self.source} - {self.event_type}"


# ============================================
# KNOWLEDGE STORAGE MODELS (PythonAnywhere)
# ============================================

class LearnedKnowledge(models.Model):
    """
    Store learned Q&A pairs in database
    Works on PythonAnywhere, Heroku, any hosting
    """
    question = models.TextField(unique=True, db_index=True)
    answer = models.TextField()
    source = models.CharField(max_length=50, default='live_call', db_index=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learned_knowledge'
        verbose_name = "Learned Knowledge"
        verbose_name_plural = "Learned Knowledge"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['question'], name='idx_question'),
            models.Index(fields=['source', '-created_at'], name='idx_source_created'),
        ]
    
    def __str__(self):
        return f"{self.question[:50]}... → {self.answer[:50]}..."


class CallConversation(models.Model):
    """
    Store complete call conversations
    For analytics and training
    """
    call_sid = models.CharField(max_length=50, unique=True, db_index=True)
    customer_phone = models.CharField(max_length=20)
    agent_id = models.CharField(max_length=50, null=True, blank=True)
    conversation_data = models.JSONField(help_text="Full conversation transcript")
    qa_pairs_count = models.IntegerField(default=0)
    duration_seconds = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default='completed')
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'call_conversations'
        verbose_name = "Call Conversation"
        verbose_name_plural = "Call Conversations"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Call {self.call_sid} - {self.qa_pairs_count} Q&A pairs"


class TrainingDocument(models.Model):
    """
    Store uploaded training documents
    PDF, Word, TXT files
    """
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=10)  # pdf, docx, txt
    content = models.TextField(help_text="Extracted text content")
    chunks_count = models.IntegerField(default=0)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'training_documents'
        verbose_name = "Training Document"
        verbose_name_plural = "Training Documents"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.file_type})"


# ============================
# AUTO-SYNC TO HUMEAI
# ============================

@receiver(post_save, sender=HumeAgent)
def sync_agent_to_humeai(sender, instance, created, **kwargs):
    """
    AUTO-SYNC: Database → HumeAI Cloud Config
    
    When you update agent in database:
    1. sales_script_text
    2. business_info (company, features, pricing)
    3. knowledge_files (Q&A, product details)
    
    → This signal automatically updates HumeAI config via API
    → Next call uses updated prompt immediately
    
    Skip conditions:
    - New agent creation (handled by create_agent() API)
    - Agent without hume_config_id
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Skip if:
    # 1. New agent creation (handled separately)
    # 2. No HumeAI config ID yet
    if created or not instance.hume_config_id:
        return
    
    try:
        # Import here to avoid circular imports
        from .hume_agent_service import hume_agent_service
        
        # Build intelligent prompt from current database state
        enhanced_prompt = hume_agent_service._build_system_prompt(
            instance.system_prompt,
            instance
        )
        
        # Update HumeAI config via API
        success = hume_agent_service.update_agent(
            config_id=instance.hume_config_id,
            name=instance.name,
            system_prompt=enhanced_prompt,
            voice_name=instance.voice_name,
            language=instance.language
        )
        
        if success:
            logger.info(f"✅ AUTO-SYNC: Updated '{instance.name}' on HumeAI")
        else:
            logger.error(f"❌ AUTO-SYNC FAILED: '{instance.name}' - API returned error")
            
    except Exception as e:
        logger.error(f"❌ AUTO-SYNC ERROR for agent {instance.id}: {str(e)}")


# ═══════════════════════════════════════════════════════════
# 📊 CLARIFIES-BASED CONVERSATION ANALYTICS MODELS
# ═══════════════════════════════════════════════════════════

class CallObjection(models.Model):
    """
    Tracks objections raised during sales calls
    
    CLARIFIES Framework:
    C - Concern identification
    L - Listen actively
    A - Acknowledge feelings
    R - Respond with empathy
    I - Inform with facts
    F - Find solutions
    I - Involve customer
    E - Ensure understanding
    S - Seal the deal
    """
    
    OBJECTION_TYPES = [
        ('price', 'Price/Budget'),
        ('timing', 'Timing/Not Ready'),
        ('competition', 'Competitor Comparison'),
        ('authority', 'Need Approval'),
        ('need', 'No Perceived Need'),
        ('trust', 'Trust/Credibility'),
        ('feature', 'Missing Feature'),
        ('support', 'Support Concerns'),
        ('contract', 'Contract Terms'),
        ('other', 'Other'),
    ]
    
    RESOLUTION_STATUS = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('unresolved', 'Unresolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.ForeignKey(
        'TwilioCall',
        on_delete=models.CASCADE,
        related_name='objections'
    )
    
    # Objection Details
    objection_type = models.CharField(max_length=20, choices=OBJECTION_TYPES)
    objection_text = models.TextField(help_text="Customer's objection statement")
    detected_at = models.DateTimeField(default=timezone.now)
    
    # CLARIFIES Response
    clarifies_step = models.CharField(
        max_length=50,
        help_text="Which CLARIFIES step was used to address this"
    )
    agent_response = models.TextField(help_text="How agent responded")
    
    # Outcome
    resolution_status = models.CharField(
        max_length=20,
        choices=RESOLUTION_STATUS,
        default='pending'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    confidence_score = models.FloatField(
        default=0.0,
        help_text="AI confidence in objection detection (0-1)"
    )
    sentiment_before = models.CharField(max_length=20, blank=True)
    sentiment_after = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['call', 'objection_type']),
            models.Index(fields=['resolution_status']),
        ]
    
    def __str__(self):
        return f"{self.objection_type} - {self.call.call_sid[:8]}"


class CLARIFIESStep(models.Model):
    """
    Tracks step-by-step CLARIFIES logic flow for each conversation
    """
    
    STEP_TYPES = [
        ('C', 'Concern - Identify customer concern'),
        ('L', 'Listen - Active listening'),
        ('A', 'Acknowledge - Acknowledge feelings'),
        ('R', 'Respond - Respond with empathy'),
        ('I', 'Inform - Provide information'),
        ('F', 'Find - Find solutions'),
        ('I2', 'Involve - Involve customer in solution'),
        ('E', 'Ensure - Ensure understanding'),
        ('S', 'Seal - Close the deal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.ForeignKey(
        'TwilioCall',
        on_delete=models.CASCADE,
        related_name='clarifies_steps'
    )
    objection = models.ForeignKey(
        CallObjection,
        on_delete=models.CASCADE,
        related_name='clarifies_steps',
        null=True,
        blank=True
    )
    
    # Step Details
    step_type = models.CharField(max_length=2, choices=STEP_TYPES)
    step_number = models.IntegerField(help_text="Sequential step number in conversation")
    
    # Content
    customer_message = models.TextField(blank=True)
    agent_message = models.TextField(blank=True)
    reasoning = models.TextField(help_text="Why this step was chosen")
    
    # Timing
    timestamp = models.DateTimeField(default=timezone.now)
    duration_seconds = models.IntegerField(default=0)
    
    # Decision Logic
    decision_factors = models.JSONField(
        default=dict,
        help_text="Factors that led to this step: sentiment, keywords, context"
    )
    alternative_paths = models.JSONField(
        default=list,
        help_text="Other possible steps that were considered"
    )
    
    # Effectiveness
    effectiveness_score = models.FloatField(
        default=0.0,
        help_text="How effective was this step (0-1)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['call', 'step_number']
        indexes = [
            models.Index(fields=['call', 'step_number']),
            models.Index(fields=['step_type']),
        ]
    
    def __str__(self):
        return f"{self.get_step_type_display()} - Step {self.step_number}"


class ConversationAnalytics(models.Model):
    """
    Aggregated analytics for each call using CLARIFIES framework
    """
    
    CALL_OUTCOME = [
        ('won', 'Won - Sale Closed'),
        ('lost', 'Lost - Not Interested'),
        ('follow_up', 'Follow-up Scheduled'),
        ('escalated', 'Escalated to Human'),
        ('incomplete', 'Call Incomplete'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(
        'TwilioCall',
        on_delete=models.CASCADE,
        related_name='clarifies_analytics'
    )
    
    # Overall Outcome
    outcome = models.CharField(max_length=20, choices=CALL_OUTCOME, default='incomplete')
    win_probability = models.FloatField(default=0.0, help_text="Predicted win rate (0-1)")
    
    # Objection Handling
    total_objections = models.IntegerField(default=0)
    objections_resolved = models.IntegerField(default=0)
    objections_escalated = models.IntegerField(default=0)
    
    # CLARIFIES Flow
    clarifies_steps_used = models.JSONField(
        default=list,
        help_text="List of CLARIFIES steps used in order"
    )
    total_steps = models.IntegerField(default=0)
    
    # Conversation Quality
    avg_sentiment = models.FloatField(default=0.0)
    sentiment_trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'Improving'),
            ('declining', 'Declining'),
            ('stable', 'Stable'),
        ],
        default='stable'
    )
    
    # Engagement Metrics
    customer_talk_time_seconds = models.IntegerField(default=0)
    agent_talk_time_seconds = models.IntegerField(default=0)
    total_turns = models.IntegerField(default=0, help_text="Number of back-and-forth exchanges")
    
    # Tone Analysis
    dominant_customer_emotion = models.CharField(max_length=50, blank=True)
    emotion_breakdown = models.JSONField(
        default=dict,
        help_text="Distribution of emotions throughout call"
    )
    
    # Decision Points
    key_decision_moments = models.JSONField(
        default=list,
        help_text="Critical moments that influenced outcome"
    )
    
    # Timestamps
    analyzed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Conversation Analytics"
        indexes = [
            models.Index(fields=['outcome']),
            models.Index(fields=['analyzed_at']),
        ]
    
    def __str__(self):
        return f"Analytics: {self.call.call_sid[:8]} - {self.outcome}"
    
    @property
    def resolution_rate(self):
        """Calculate objection resolution rate"""
        if self.total_objections == 0:
            return 0.0
        return (self.objections_resolved / self.total_objections) * 100


class RiskFlag(models.Model):
    """
    Flags potentially risky content before it's sent to customer
    Regex-based filter for compliance and safety
    """
    
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('auto_blocked', 'Auto-Blocked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.ForeignKey(
        'TwilioCall',
        on_delete=models.CASCADE,
        related_name='risk_flags'
    )
    
    # Content
    flagged_content = models.TextField(help_text="The content that was flagged")
    flag_reason = models.TextField(help_text="Why this content was flagged")
    matched_pattern = models.CharField(max_length=255, help_text="Regex pattern that matched")
    
    # Risk Assessment
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    risk_category = models.CharField(
        max_length=50,
        help_text="e.g., profanity, legal_claim, medical_advice"
    )
    
    # Action Taken
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    was_blocked = models.BooleanField(default=True, help_text="Was message blocked from customer?")
    replacement_sent = models.TextField(
        blank=True,
        help_text="Alternative message sent if blocked"
    )
    
    # Review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_flags'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Timestamps
    detected_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['call', 'detected_at']),
            models.Index(fields=['status', 'risk_level']),
            models.Index(fields=['risk_category']),
        ]
    
    def __str__(self):
        return f"{self.risk_level} - {self.risk_category} ({self.call.call_sid[:8]})"

