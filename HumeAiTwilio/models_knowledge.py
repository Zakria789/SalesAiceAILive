"""
Django Models for Knowledge Storage (PythonAnywhere Compatible)
"""
from django.db import models
from django.utils import timezone

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
        verbose_name = "Learned Knowledge"
        verbose_name_plural = "Learned Knowledge"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['source', '-created_at']),
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
        verbose_name = "Training Document"
        verbose_name_plural = "Training Documents"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.file_type})"
