"""
Intelligent Response Service
1. Check prompt/knowledge base first
2. If no answer found, perform web search
3. Learn and save customer information
"""

import logging
import re
import requests
from typing import Optional, Dict, Any, Tuple
from django.utils import timezone
from .models import LearnedKnowledge, CustomerProfile, TwilioCall

logger = logging.getLogger(__name__)


class IntelligentResponseService:
    """
    Handles intelligent response generation and customer learning
    """
    
    def __init__(self, call: TwilioCall = None):
        self.call = call
        self.customer_profile = None
        if call and call.to_number:
            self.customer_profile = self._get_or_create_customer_profile(call.to_number)
    
    def _get_or_create_customer_profile(self, phone_number: str) -> Optional[CustomerProfile]:
        """Get existing customer profile or create new one"""
        try:
            profile, created = CustomerProfile.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'total_calls': 0,
                    'learned_preferences': {},
                    'previous_topics': [],
                    'custom_fields': {}
                }
            )
            if created:
                logger.info(f"✨ [NEW CUSTOMER] Created profile for {phone_number}")
            else:
                logger.info(f"👤 [EXISTING CUSTOMER] Found profile: {profile.full_name or 'Unknown'}")
            return profile
        except Exception as e:
            logger.error(f"❌ Error getting customer profile: {e}")
            return None
    
    def extract_customer_name_from_message(self, message: str) -> Optional[str]:
        """
        Extract customer name from conversation
        Patterns: "My name is...", "I am...", "This is...", "It's..."
        """
        try:
            message_lower = message.lower()
            
            # Pattern 1: "my name is [name]"
            match = re.search(r'my name is ([a-z\s]+)', message_lower)
            if match:
                return match.group(1).strip().title()
            
            # Pattern 2: "i am [name]" / "i'm [name]"
            match = re.search(r"i['\s]?am ([a-z\s]+)", message_lower)
            if match:
                name = match.group(1).strip()
                # Avoid common false positives
                if name not in ['calling', 'looking', 'interested', 'fine', 'good', 'here']:
                    return name.title()
            
            # Pattern 3: "this is [name]"
            match = re.search(r'this is ([a-z\s]+)', message_lower)
            if match:
                name = match.group(1).strip()
                if len(name.split()) <= 3:  # Limit to max 3 words
                    return name.title()
            
            # Pattern 4: "[Name] speaking"
            match = re.search(r'^([a-z\s]{2,20}) speaking', message_lower)
            if match:
                return match.group(1).strip().title()
            
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting name: {e}")
            return None
    
    def update_customer_info(self, message: str, role: str = 'user'):
        """
        Update customer profile based on conversation
        Learns name, preferences, topics automatically
        """
        try:
            if not self.customer_profile or role != 'user':
                return
            
            updated = False
            
            # 1. Extract and save customer name
            if not self.customer_profile.full_name:
                extracted_name = self.extract_customer_name_from_message(message)
                if extracted_name:
                    self.customer_profile.full_name = extracted_name
                    updated = True
                    logger.info(f"✅ [LEARNED NAME] Customer name: {extracted_name}")
            
            # 2. Extract email if mentioned
            if not self.customer_profile.email:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
                if email_match:
                    self.customer_profile.email = email_match.group(0)
                    updated = True
                    logger.info(f"✅ [LEARNED EMAIL] {self.customer_profile.email}")
            
            # 3. Extract company if mentioned
            if not self.customer_profile.company:
                company_patterns = [
                    r'i work at ([\w\s]+)',
                    r'i[\'m]? from ([\w\s]+) company',
                    r'represent(?:ing)? ([\w\s]+)',
                ]
                for pattern in company_patterns:
                    match = re.search(pattern, message.lower())
                    if match:
                        self.customer_profile.company = match.group(1).strip().title()
                        updated = True
                        logger.info(f"✅ [LEARNED COMPANY] {self.customer_profile.company}")
                        break
            
            # 4. Track topics discussed
            if self.customer_profile.previous_topics is None:
                self.customer_profile.previous_topics = []
            
            # Simple topic extraction (keywords)
            topics = ['billing', 'pricing', 'support', 'sales', 'demo', 'trial', 
                     'refund', 'cancel', 'upgrade', 'features', 'integration']
            
            for topic in topics:
                if topic in message.lower():
                    if topic not in self.customer_profile.previous_topics:
                        self.customer_profile.previous_topics.append(topic)
                        updated = True
                        logger.info(f"📝 [TOPIC TRACKED] {topic}")
            
            # 5. Update last call date and total calls
            self.customer_profile.last_call_date = timezone.now()
            self.customer_profile.total_calls += 1
            
            if updated:
                self.customer_profile.save()
                logger.info(f"💾 [PROFILE UPDATED] {self.customer_profile.full_name or self.customer_profile.phone_number}")
            
            # Link profile to call
            if self.call and not self.call.customer_profile:
                self.call.customer_profile = self.customer_profile
                self.call.customer_name = self.customer_profile.full_name
                self.call.customer_email = self.customer_profile.email
                self.call.save()
        
        except Exception as e:
            logger.error(f"❌ Error updating customer info: {e}")
    
    def search_knowledge_base(self, query: str) -> Optional[str]:
        """
        🔍 Smart search in knowledge base with synonym matching
        Understands different ways to ask same question
        """
        try:
            query_lower = query.lower().strip()
            
            # 🎯 SYNONYM GROUPS - Different ways to ask same thing
            synonyms = {
                'price': ['cost', 'price', 'pricing', 'expensive', 'fee', 'charge', 'payment'],
                'features': ['do', 'does', 'feature', 'function', 'capability', 'work', 'about'],
                'small': ['small', 'startup', 'little', 'tiny', 'mid-sized'],
                'business': ['business', 'company', 'firm', 'organization', 'team'],
                'try': ['try', 'test', 'demo', 'trial', 'sample'],
                'integrate': ['integrate', 'work with', 'connect', 'sync', 'compatible'],
            }
            
            # Expand query with synonyms
            expanded_words = set(query_lower.split())
            for word in query_lower.split():
                for key, syn_list in synonyms.items():
                    if word in syn_list:
                        expanded_words.update(syn_list)
            
            # Get all knowledge entries
            knowledge_entries = LearnedKnowledge.objects.all()
            
            best_match = None
            best_score = 0
            
            for entry in knowledge_entries:
                question_lower = entry.question.lower()
                question_words = set(question_lower.split())
                
                # Calculate similarity with synonym expansion
                common_words = expanded_words & question_words
                score = len(common_words) / max(len(expanded_words), len(question_words))
                
                # Boost score if key words match
                if 'cost' in query_lower or 'price' in query_lower:
                    if 'cost' in question_lower or 'price' in question_lower:
                        score += 0.3
                
                if 'small' in query_lower and 'business' in query_lower:
                    if 'small' in question_lower and 'business' in question_lower:
                        score += 0.3
                
                if score > best_score and score > 0.4:  # 40% threshold (more lenient)
                    best_score = score
                    best_match = entry
            
            if best_match:
                logger.info(f"✅ [KNOWLEDGE FOUND] Similarity: {best_score:.2f}")
                logger.info(f"   Question: {best_match.question[:50]}...")
                logger.info(f"   Answer: {best_match.answer[:100]}...")
                return best_match.answer
            
            logger.info(f"❌ [NO MATCH] No knowledge found for: {query[:50]}...")
            return None
        
        except Exception as e:
            logger.error(f"❌ Error searching knowledge base: {e}")
            return None
    
    def web_search(self, query: str) -> Optional[str]:
        """
        Perform web search using DuckDuckGo Instant Answer API (free, no API key)
        Falls back to simple search if API fails
        """
        try:
            logger.info(f"🔍 [WEB SEARCH] Searching for: {query}")
            
            # DuckDuckGo Instant Answer API (free, no key required)
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Try Abstract first (best answer)
                if data.get('Abstract'):
                    answer = data['Abstract']
                    logger.info(f"✅ [FOUND] Web answer: {answer[:100]}...")
                    
                    # Save to knowledge base for future
                    LearnedKnowledge.objects.get_or_create(
                        question=query,
                        defaults={
                            'answer': answer,
                            'source': 'web_search',
                            'metadata': {'search_engine': 'duckduckgo'}
                        }
                    )
                    return answer
                
                # Try RelatedTopics if Abstract empty
                if data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                    first_topic = data['RelatedTopics'][0]
                    if isinstance(first_topic, dict) and 'Text' in first_topic:
                        answer = first_topic['Text']
                        logger.info(f"✅ [FOUND] Related topic: {answer[:100]}...")
                        
                        LearnedKnowledge.objects.get_or_create(
                            question=query,
                            defaults={
                                'answer': answer,
                                'source': 'web_search',
                                'metadata': {'search_engine': 'duckduckgo'}
                            }
                        )
                        return answer
            
            logger.warning(f"⚠️  [NO RESULTS] Web search returned no results")
            return None
        
        except Exception as e:
            logger.error(f"❌ [SEARCH ERROR] Web search failed: {e}")
            return None
    
    def get_intelligent_response(self, user_question: str) -> Tuple[str, str]:
        """
        Get intelligent response with fallback chain:
        1. Check knowledge base
        2. If not found, perform web search
        3. Return response + source
        
        Returns: (answer, source)
        """
        try:
            # Step 1: Check knowledge base
            answer = self.search_knowledge_base(user_question)
            if answer:
                return (answer, 'knowledge_base')
            
            # Step 2: Web search fallback
            answer = self.web_search(user_question)
            if answer:
                return (answer, 'web_search')
            
            # Step 3: Default response
            return (
                "I don't have that specific information right now, but I'd be happy to help you find it. Could you provide more details or rephrase your question?",
                'default'
            )
        
        except Exception as e:
            logger.error(f"❌ Error in intelligent response: {e}")
            return (
                "I apologize, I'm having trouble processing that right now. Can you try asking in a different way?",
                'error'
            )
    
    def get_customer_context(self) -> str:
        """
        Get customer context for personalized greeting
        Returns context string to include in HumeAI prompt
        """
        if not self.customer_profile:
            return ""
        
        context_parts = []
        
        if self.customer_profile.full_name:
            context_parts.append(f"Customer Name: {self.customer_profile.full_name}")
        
        if self.customer_profile.total_calls > 1:
            context_parts.append(f"Previous Calls: {self.customer_profile.total_calls - 1}")
        
        if self.customer_profile.previous_topics:
            topics = ", ".join(self.customer_profile.previous_topics[-3:])  # Last 3 topics
            context_parts.append(f"Previously Discussed: {topics}")
        
        if self.customer_profile.company:
            context_parts.append(f"Company: {self.customer_profile.company}")
        
        if context_parts:
            return "\n".join([
                "📋 CUSTOMER CONTEXT:",
                *context_parts,
                ""
            ])
        
        return ""
