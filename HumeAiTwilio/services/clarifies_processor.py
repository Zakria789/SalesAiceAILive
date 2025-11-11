"""
🎯 CLARIFIES Sales Framework Processor

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

This service:
1. Analyzes conversation messages in real-time
2. Detects sales objections
3. Determines appropriate CLARIFIES step
4. Tracks decision-making logic
5. Provides explainable AI reasoning
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


class CLARIFIESProcessor:
    """
    Processes conversation messages through CLARIFIES framework
    """
    
    # Objection Detection Patterns
    OBJECTION_PATTERNS = {
        'price': [
            r'\b(too expensive|costly|afford|budget|price|cheap|money)\b',
            r'\b(cost too much|can\'t pay|overpriced)\b',
        ],
        'timing': [
            r'\b(not ready|maybe later|call back|another time|next month)\b',
            r'\b(busy|not now|timing|wait)\b',
        ],
        'competition': [
            r'\b(competitor|already using|other option|compare|alternative)\b',
            r'\b(better deal|someone else)\b',
        ],
        'authority': [
            r'\b(need approval|ask my|boss|manager|team|decision)\b',
            r'\b(not authorized|can\'t decide alone)\b',
        ],
        'need': [
            r'\b(don\'t need|not interested|no use|don\'t want)\b',
            r'\b(happy with|satisfied|works fine)\b',
        ],
        'trust': [
            r'\b(don\'t trust|scam|skeptical|doubt|proof|guarantee)\b',
            r'\b(too good to be true|suspicious)\b',
        ],
        'feature': [
            r'\b(missing|lack|doesn\'t have|need to|must have)\b',
            r'\b(feature|functionality|capability)\b',
        ],
        'support': [
            r'\b(support|help|training|onboarding|documentation)\b',
            r'\b(technical|customer service)\b',
        ],
        'contract': [
            r'\b(contract|terms|cancellation|commitment|lock-in)\b',
            r'\b(fine print|hidden fees)\b',
        ],
    }
    
    # Sentiment Keywords
    POSITIVE_KEYWORDS = [
        'great', 'good', 'excellent', 'perfect', 'amazing', 'love',
        'interested', 'helpful', 'thank', 'appreciate', 'yes', 'sure'
    ]
    
    NEGATIVE_KEYWORDS = [
        'no', 'not', 'never', 'bad', 'terrible', 'awful', 'hate',
        'disappointed', 'frustrated', 'angry', 'confused', 'problem'
    ]
    
    # CLARIFIES Step Determination Logic
    STEP_RULES = {
        'C': {  # Concern - First interaction or new objection
            'triggers': ['objection_detected', 'new_topic', 'question_asked'],
            'next_steps': ['L', 'A', 'I']
        },
        'L': {  # Listen - Customer is speaking, need to understand
            'triggers': ['customer_explaining', 'long_message', 'emotion_high'],
            'next_steps': ['A', 'R']
        },
        'A': {  # Acknowledge - Show understanding of feelings
            'triggers': ['emotion_detected', 'frustration', 'concern_expressed'],
            'next_steps': ['R', 'I']
        },
        'R': {  # Respond - Empathetic response
            'triggers': ['need_empathy', 'emotional_support'],
            'next_steps': ['I', 'F']
        },
        'I': {  # Inform - Provide information/facts
            'triggers': ['question', 'information_needed', 'clarification'],
            'next_steps': ['F', 'E', 'I2']
        },
        'F': {  # Find solutions
            'triggers': ['objection_resolved', 'options_needed'],
            'next_steps': ['I2', 'E']
        },
        'I2': {  # Involve customer
            'triggers': ['customer_engagement', 'decision_time'],
            'next_steps': ['E', 'S']
        },
        'E': {  # Ensure understanding
            'triggers': ['confirmation_needed', 'clarity_check'],
            'next_steps': ['S', 'F']
        },
        'S': {  # Seal the deal
            'triggers': ['ready_to_close', 'positive_sentiment', 'agreement'],
            'next_steps': ['complete']
        }
    }
    
    def __init__(self, call):
        """
        Initialize processor for a specific call
        
        Args:
            call: TwilioCall instance
        """
        self.call = call
        self.conversation_history = []
        self.current_step = 'C'  # Start with Concern identification
        self.objection_count = 0
        self.sentiment_trend = []
    
    def process_message(
        self,
        message: str,
        speaker: str,
        timestamp: Optional[timezone.datetime] = None
    ) -> Dict:
        """
        Process a single message through CLARIFIES framework
        
        Args:
            message: Message text
            speaker: 'customer' or 'agent'
            timestamp: Message timestamp
        
        Returns:
            Dict with:
            - objection_detected: bool
            - objection_type: str or None
            - recommended_step: str
            - reasoning: str
            - sentiment: str
            - confidence: float
        """
        if timestamp is None:
            timestamp = timezone.now()
        
        # Add to conversation history
        self.conversation_history.append({
            'message': message,
            'speaker': speaker,
            'timestamp': timestamp
        })
        
        result = {
            'objection_detected': False,
            'objection_type': None,
            'recommended_step': self.current_step,
            'reasoning': '',
            'sentiment': 'neutral',
            'confidence': 0.0,
            'triggers': []
        }
        
        # Only analyze customer messages for objections
        if speaker == 'customer':
            # Detect objection
            objection_type, confidence = self._detect_objection(message)
            if objection_type:
                result['objection_detected'] = True
                result['objection_type'] = objection_type
                result['confidence'] = confidence
                self.objection_count += 1
            
            # Analyze sentiment
            result['sentiment'] = self._analyze_sentiment(message)
            self.sentiment_trend.append(result['sentiment'])
            
            # Determine next CLARIFIES step
            next_step, reasoning, triggers = self._determine_next_step(
                message,
                result['objection_detected'],
                result['sentiment']
            )
            
            result['recommended_step'] = next_step
            result['reasoning'] = reasoning
            result['triggers'] = triggers
            self.current_step = next_step
        
        return result
    
    def _detect_objection(self, message: str) -> Tuple[Optional[str], float]:
        """
        Detect objection type using regex patterns
        
        Returns:
            (objection_type, confidence_score)
        """
        message_lower = message.lower()
        
        # Check each objection type
        best_match = None
        max_matches = 0
        
        for objection_type, patterns in self.OBJECTION_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    matches += 1
            
            if matches > max_matches:
                max_matches = matches
                best_match = objection_type
        
        if best_match:
            # Calculate confidence (simple approach - can be enhanced)
            confidence = min(max_matches / len(self.OBJECTION_PATTERNS[best_match]), 1.0)
            return best_match, confidence
        
        return None, 0.0
    
    def _analyze_sentiment(self, message: str) -> str:
        """
        Simple keyword-based sentiment analysis
        
        Returns:
            'positive', 'negative', or 'neutral'
        """
        message_lower = message.lower()
        
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in message_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in message_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _determine_next_step(
        self,
        message: str,
        objection_detected: bool,
        sentiment: str
    ) -> Tuple[str, str, List[str]]:
        """
        Determine next CLARIFIES step based on context
        
        Returns:
            (step_code, reasoning, triggers)
        """
        triggers = []
        
        # Check for specific triggers
        message_lower = message.lower()
        
        # New objection detected
        if objection_detected:
            triggers.append('objection_detected')
            step = 'C'  # Go back to Concern identification
            reasoning = f"New objection detected. Starting CLARIFIES process."
        
        # Question asked
        elif '?' in message:
            triggers.append('question_asked')
            step = 'I'  # Provide information
            reasoning = "Customer asked a question. Need to inform with relevant information."
        
        # High emotion
        elif sentiment == 'negative':
            triggers.append('emotion_high')
            step = 'A'  # Acknowledge feelings
            reasoning = "Negative sentiment detected. Need to acknowledge customer's feelings."
        
        # Positive sentiment - moving towards close
        elif sentiment == 'positive' and self.current_step in ['I', 'F', 'E']:
            triggers.append('positive_sentiment')
            step = 'S'  # Try to seal
            reasoning = "Positive sentiment and advanced stage. Ready to close."
        
        # Long message - customer explaining
        elif len(message.split()) > 15:
            triggers.append('customer_explaining')
            step = 'L'  # Listen actively
            reasoning = "Customer providing detailed explanation. Active listening required."
        
        # Default: follow natural progression
        else:
            current_rules = self.STEP_RULES.get(self.current_step, {'next_steps': ['I']})
            step = current_rules['next_steps'][0] if current_rules['next_steps'] else 'I'
            reasoning = f"Following natural CLARIFIES progression from {self.current_step} to {step}."
            triggers.append('natural_progression')
        
        return step, reasoning, triggers
    
    @transaction.atomic
    def save_objection(
        self,
        objection_type: str,
        objection_text: str,
        agent_response: str,
        clarifies_step: str,
        confidence: float,
        sentiment: str
    ) -> 'CallObjection':
        """
        Save detected objection to database
        """
        from HumeAiTwilio.models import CallObjection
        
        objection = CallObjection.objects.create(
            call=self.call,
            objection_type=objection_type,
            objection_text=objection_text,
            agent_response=agent_response,
            clarifies_step=clarifies_step,
            confidence_score=confidence,
            sentiment_before=sentiment,
            resolution_status='pending'
        )
        
        logger.info(f"✅ Saved objection: {objection_type} for call {self.call.call_sid[:8]}")
        return objection
    
    @transaction.atomic
    def save_clarifies_step(
        self,
        step_type: str,
        customer_message: str,
        agent_message: str,
        reasoning: str,
        decision_factors: Dict,
        effectiveness_score: float = 0.0,
        objection=None
    ) -> 'CLARIFIESStep':
        """
        Save CLARIFIES step to database
        """
        from HumeAiTwilio.models import CLARIFIESStep
        
        # Get current step number
        last_step = CLARIFIESStep.objects.filter(call=self.call).order_by('-step_number').first()
        step_number = (last_step.step_number + 1) if last_step else 1
        
        step = CLARIFIESStep.objects.create(
            call=self.call,
            objection=objection,
            step_type=step_type,
            step_number=step_number,
            customer_message=customer_message,
            agent_message=agent_message,
            reasoning=reasoning,
            decision_factors=decision_factors,
            effectiveness_score=effectiveness_score
        )
        
        logger.info(f"✅ Saved CLARIFIES step {step_number}: {step_type}")
        return step
    
    def get_analytics_summary(self) -> Dict:
        """
        Generate analytics summary for the call
        """
        total_messages = len(self.conversation_history)
        customer_messages = len([m for m in self.conversation_history if m['speaker'] == 'customer'])
        agent_messages = len([m for m in self.conversation_history if m['speaker'] == 'agent'])
        
        # Calculate sentiment trend
        if len(self.sentiment_trend) >= 2:
            first_half = self.sentiment_trend[:len(self.sentiment_trend)//2]
            second_half = self.sentiment_trend[len(self.sentiment_trend)//2:]
            
            positive_first = first_half.count('positive')
            positive_second = second_half.count('positive')
            
            if positive_second > positive_first:
                sentiment_trend = 'improving'
            elif positive_second < positive_first:
                sentiment_trend = 'declining'
            else:
                sentiment_trend = 'stable'
        else:
            sentiment_trend = 'stable'
        
        return {
            'total_messages': total_messages,
            'customer_messages': customer_messages,
            'agent_messages': agent_messages,
            'total_objections': self.objection_count,
            'sentiment_trend': sentiment_trend,
            'conversation_history': self.conversation_history,
        }


def get_step_display_name(step_code: str) -> str:
    """Get human-readable CLARIFIES step name"""
    step_names = {
        'C': 'Concern - Identify customer concern',
        'L': 'Listen - Active listening',
        'A': 'Acknowledge - Acknowledge feelings',
        'R': 'Respond - Respond with empathy',
        'I': 'Inform - Provide information',
        'F': 'Find - Find solutions',
        'I2': 'Involve - Involve customer in solution',
        'E': 'Ensure - Ensure understanding',
        'S': 'Seal - Close the deal',
    }
    return step_names.get(step_code, step_code)
