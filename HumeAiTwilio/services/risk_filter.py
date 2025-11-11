"""
🛡️ Risk Filter System

Regex-based content filtering to prevent:
- Profanity/offensive language
- False claims/misleading statements
- Medical/legal advice
- Personal information leaks
- Compliance violations

Runs BEFORE agent response is sent to customer.
If flagged, content is logged and blocked.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


class RiskFilter:
    """
    Filters potentially risky content using regex patterns
    """
    
    # Risk Patterns (can be extended/customized)
    RISK_PATTERNS = {
        'profanity': {
            'level': 'high',
            'patterns': [
                r'\b(fuck|shit|damn|bitch|asshole|bastard)\w*\b',
                r'\b(crap|hell)\b',
            ],
            'block': True,
            'replacement': "I apologize, let me rephrase that in a more professional manner."
        },
        
        'legal_claim': {
            'level': 'critical',
            'patterns': [
                r'\b(guaranteed|promise|will definitely|100% sure|legally binding)\b',
                r'\b(no risk|risk-free|cannot lose)\b',
                r'\b(lawsuit|sue|legal action)\b',
            ],
            'block': True,
            'replacement': "Based on our terms and conditions, we can discuss the available options."
        },
        
        'medical_advice': {
            'level': 'critical',
            'patterns': [
                r'\b(cure|treat|diagnose|medical condition|disease|illness)\b',
                r'\b(doctor|physician|prescription|medication)\b',
            ],
            'block': True,
            'replacement': "I recommend consulting with a qualified healthcare professional for medical guidance."
        },
        
        'personal_info_leak': {
            'level': 'critical',
            'patterns': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
                r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email (not agent's)
                r'\b\d{16}\b',  # Credit card
                r'\b(password|pin|secret key)\b',
            ],
            'block': True,
            'replacement': "For security reasons, please don't share sensitive personal information over the call."
        },
        
        'false_urgency': {
            'level': 'medium',
            'patterns': [
                r'\b(only today|last chance|expires now|limited spots|act fast)\b',
                r'\b(urgent|hurry|immediately|right now)\b',
            ],
            'block': False,  # Just flag for review
            'replacement': None
        },
        
        'competitor_defamation': {
            'level': 'high',
            'patterns': [
                r'\b(terrible|awful|scam|fraud|lying|cheating)\b.*\b(competitor|competition)\b',
                r'\bthey (suck|fail|cheat|lie)\b',
            ],
            'block': True,
            'replacement': "While I can't comment on other companies, let me explain what makes our solution unique."
        },
        
        'financial_advice': {
            'level': 'critical',
            'patterns': [
                r'\b(investment advice|financial planning|tax strategy)\b',
                r'\b(guaranteed returns|profit|roi|earnings)\b',
            ],
            'block': True,
            'replacement': "For financial matters, I recommend consulting with a licensed financial advisor."
        },
        
        'discriminatory_language': {
            'level': 'critical',
            'patterns': [
                r'\b(race|ethnicity|religion|gender|age|disability)\b.*\b(bias|discriminat|prejudice)\b',
            ],
            'block': True,
            'replacement': "We serve all customers equally and fairly. Let me focus on how we can help you."
        },
        
        'unsubstantiated_claim': {
            'level': 'medium',
            'patterns': [
                r'\b(best in the world|number one|everyone uses|nobody else)\b',
                r'\b(always works|never fails|perfect solution)\b',
            ],
            'block': False,
            'replacement': None
        },
    }
    
    def __init__(self, call=None):
        """
        Initialize risk filter
        
        Args:
            call: TwilioCall instance (optional, for logging)
        """
        self.call = call
        self.flags_detected = []
    
    def check_content(self, content: str, speaker: str = 'agent') -> Dict:
        """
        Check content for risk patterns
        
        Args:
            content: Text to check
            speaker: 'agent' or 'customer'
        
        Returns:
            Dict with:
            - is_risky: bool
            - should_block: bool
            - risk_flags: List[Dict]
            - safe_content: str (original or replacement)
            - highest_risk_level: str
        """
        result = {
            'is_risky': False,
            'should_block': False,
            'risk_flags': [],
            'safe_content': content,
            'highest_risk_level': 'low'
        }
        
        content_lower = content.lower()
        
        # Check each risk category
        for category, config in self.RISK_PATTERNS.items():
            for pattern in config['patterns']:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    # Risk detected
                    result['is_risky'] = True
                    
                    flag_info = {
                        'category': category,
                        'risk_level': config['level'],
                        'matched_pattern': pattern,
                        'should_block': config['block']
                    }
                    
                    result['risk_flags'].append(flag_info)
                    
                    # Update highest risk level
                    if self._compare_risk_levels(config['level'], result['highest_risk_level']) > 0:
                        result['highest_risk_level'] = config['level']
                    
                    # Check if should block
                    if config['block']:
                        result['should_block'] = True
                        if config['replacement']:
                            result['safe_content'] = config['replacement']
                    
                    # Log flag
                    if self.call:
                        self._log_risk_flag(
                            content,
                            category,
                            pattern,
                            config['level'],
                            config['block'],
                            config['replacement']
                        )
                    
                    # Stop checking patterns for this category once matched
                    break
        
        return result
    
    def _compare_risk_levels(self, level1: str, level2: str) -> int:
        """
        Compare two risk levels
        
        Returns:
            1 if level1 > level2
            0 if equal
            -1 if level1 < level2
        """
        level_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        return level_order.get(level1, 0) - level_order.get(level2, 0)
    
    @transaction.atomic
    def _log_risk_flag(
        self,
        content: str,
        category: str,
        pattern: str,
        risk_level: str,
        blocked: bool,
        replacement: Optional[str]
    ):
        """
        Log risk flag to database
        """
        from HumeAiTwilio.models import RiskFlag
        
        try:
            flag = RiskFlag.objects.create(
                call=self.call,
                flagged_content=content,
                flag_reason=f"Matched {category} risk pattern",
                matched_pattern=pattern,
                risk_level=risk_level,
                risk_category=category,
                was_blocked=blocked,
                replacement_sent=replacement or '',
                status='auto_blocked' if blocked else 'pending'
            )
            
            logger.warning(
                f"⚠️  Risk flag detected: {category} (level: {risk_level}) "
                f"- Call: {self.call.call_sid[:8]} - Blocked: {blocked}"
            )
            
            self.flags_detected.append(flag)
            
        except Exception as e:
            logger.error(f"❌ Error logging risk flag: {e}")
    
    def get_flagged_count(self) -> int:
        """Get number of flags detected in current session"""
        return len(self.flags_detected)
    
    @staticmethod
    def add_custom_pattern(
        category: str,
        pattern: str,
        risk_level: str = 'medium',
        block: bool = False,
        replacement: Optional[str] = None
    ):
        """
        Add custom risk pattern (for dynamic configuration)
        
        Note: This modifies class-level patterns for current session only.
        For persistent patterns, update RISK_PATTERNS dictionary.
        """
        if category not in RiskFilter.RISK_PATTERNS:
            RiskFilter.RISK_PATTERNS[category] = {
                'level': risk_level,
                'patterns': [],
                'block': block,
                'replacement': replacement
            }
        
        RiskFilter.RISK_PATTERNS[category]['patterns'].append(pattern)
        logger.info(f"✅ Added custom risk pattern: {category} - {pattern}")
    
    @staticmethod
    def get_all_patterns() -> Dict:
        """Get all configured risk patterns"""
        return RiskFilter.RISK_PATTERNS.copy()


def validate_message_safety(message: str, call=None) -> Tuple[bool, str]:
    """
    Quick helper function to validate message safety
    
    Args:
        message: Message to check
        call: TwilioCall instance (optional)
    
    Returns:
        (is_safe, safe_content)
    """
    filter = RiskFilter(call=call)
    result = filter.check_content(message)
    
    is_safe = not result['should_block']
    safe_content = result['safe_content']
    
    return is_safe, safe_content
