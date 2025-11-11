"""
🤖 HUMEAI AGENT SERVICE
=======================

Automatically sync agents with HumeAI:
1. Create agent in HumeAI when local agent is created
2. Store HumeAI config_id in local database
3. Update/delete agent in HumeAI when local agent changes
"""

import logging
import requests
from typing import Dict, Any, Optional
from decouple import config
from datetime import datetime

logger = logging.getLogger(__name__)

# HumeAI Configuration
HUME_API_KEY = config('HUME_API_KEY', default='')
HUME_API_BASE = 'https://api.hume.ai/v0'


class HumeAgentService:
    """Service to manage HumeAI agents via API"""
    
    def __init__(self):
        self.api_key = HUME_API_KEY
        self.base_url = HUME_API_BASE
        self.headers = {
            'X-Hume-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def create_agent(self, 
                     name: str,
                     system_prompt: str,
                     voice_name: str = 'ITO',
                     language: str = 'en',
                     agent_obj=None) -> Optional[str]:
        """
        Create agent in HumeAI and return config_id
        
        Args:
            name: Agent name
            system_prompt: System prompt for agent
            voice_name: Voice to use (default: ITO)
            language: Language code (default: en)
            agent_obj: Agent object from database (optional) - used to get sales_script and knowledge_base
            
        Returns:
            config_id if successful, None if failed
        """
        try:
            # 🔥 BUILD ENHANCED SYSTEM PROMPT FROM DATABASE
            enhanced_prompt = self._build_system_prompt(system_prompt, agent_obj)
            
            # HumeAI EVI API endpoint
            url = f"{self.base_url}/evi/configs"
            
            payload = {
                "name": name,
                "prompt": {
                    "text": enhanced_prompt
                },
                "voice": {
                    "provider": "HUME_AI",
                    "name": voice_name
                },
                "language": {
                    "code": language
                },
                "ellm_model": {
                    "provider": "HUME_AI",
                    "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                    "allow_short_responses": True
                },
                "builtin_tools": [
                    {
                        "name": "web_search",
                        "enabled": True
                    },
                    {
                        "name": "hang_up", 
                        "enabled": True
                    }
                ],
                "description": enhanced_prompt[:200] + "..." if len(enhanced_prompt) > 200 else enhanced_prompt
            }
            
            logger.info(f"🤖 Creating HumeAI agent: {name}")
            logger.info(f"📝 Using sales_script from DB: {bool(agent_obj and agent_obj.sales_script_text)}")
            logger.info(f"📚 Using knowledge_base from DB: {bool(agent_obj and agent_obj.business_info)}")
            logger.info(f"🔑 API Key present: {bool(self.api_key)}")
            logger.info(f"🌐 API URL: {url}")
            logger.info(f"📤 Enhanced prompt length: {len(enhanced_prompt)} chars")
            logger.info(f"📤 Prompt preview: {enhanced_prompt[:200]}...")
            logger.info(f"🛠️  Tools enabled: web_search, hang_up")
            logger.info(f"🎯 Model: {payload['ellm_model']['model']}")
            logger.info(f"📋 Full payload: {payload}")
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            
            logger.info(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                config_id = data.get('id')
                logger.info(f"✅ HumeAI agent created: {config_id}")
                logger.info(f"📊 Response data: {data}")
                return config_id
            elif response.status_code == 409:
                logger.warning(f"⚠️  Agent name '{name}' already exists in HumeAI")
                logger.warning(f"⚠️  Using unique name: {name}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                # Retry with unique name
                return self.create_agent(
                    name=f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    system_prompt=system_prompt,
                    voice_name=voice_name,
                    language=language,
                    agent_obj=agent_obj
                )
            else:
                logger.error(f"❌ Failed to create HumeAI agent: {response.status_code}")
                logger.error(f"❌ Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ HumeAI API timeout after 10 seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ HumeAI API connection error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating HumeAI agent: {str(e)}")
            logger.exception("Full traceback:")
            return None
    
    def _build_system_prompt(self, base_prompt: str, agent_obj=None) -> str:
        """
        🔥 Build intelligent system prompt using database fields
        
        Args:
            base_prompt: Base system prompt
            agent_obj: Agent object from database
            
        Returns:
            Enhanced system prompt with sales_script and intelligent Q&A handling
        """
        try:
            if not agent_obj:
                return base_prompt
            
            # Extract company name and agent name from business_info
            company_name = "our company"
            agent_name = "the sales team"
            
            if agent_obj.business_info and isinstance(agent_obj.business_info, dict):
                company_name = agent_obj.business_info.get('company_name', company_name)
            
            if agent_obj.name:
                agent_name = agent_obj.name
            
            prompt_parts = []
            
            # 🔥 HEADER
            prompt_parts.append(f"You are a professional AI sales agent calling from {company_name}.")
            
            if agent_obj.business_info and isinstance(agent_obj.business_info, dict):
                biz_desc = agent_obj.business_info.get('business_description')
                if biz_desc:
                    prompt_parts.append(f"\nCOMPANY: {company_name} - {biz_desc}")
            
            # 🔥 CALL SCRIPT (if sales_script_text exists)
            if agent_obj.sales_script_text:
                logger.info(f"📝 Adding 3-step sales script from database ({len(agent_obj.sales_script_text)} chars)")
                prompt_parts.append("\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                prompt_parts.append("CALL SCRIPT - NATURAL CONVERSATION FLOW:")
                prompt_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                prompt_parts.append("\nHOW TO USE THIS SCRIPT:")
                prompt_parts.append("• If customer LISTENS silently → Continue step-by-step")
                prompt_parts.append("• If customer INTERRUPTS → Respond to their question/comment")
                prompt_parts.append("• After answering → Continue where you left off in the script")
                prompt_parts.append("\n" + agent_obj.sales_script_text)
            
            # 🔥 KNOWLEDGE BASE (if knowledge_files or business_info exists)
            if agent_obj.knowledge_files or agent_obj.business_info:
                logger.info(f"📚 Adding knowledge base from database")
                prompt_parts.append("\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                prompt_parts.append(f"{company_name.upper()} KNOWLEDGE BASE:")
                prompt_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # Add business info
                if agent_obj.business_info and isinstance(agent_obj.business_info, dict):
                    biz = agent_obj.business_info
                    
                    if biz.get('company_website'):
                        prompt_parts.append(f"\nWebsite: {biz['company_website']}")
                    
                    if biz.get('industry'):
                        prompt_parts.append(f"Industry: {biz['industry']}")
                    
                    # Product features
                    if biz.get('product_features'):
                        prompt_parts.append("\nPRODUCT FEATURES:")
                        features = biz['product_features']
                        if isinstance(features, list):
                            for feat in features:
                                prompt_parts.append(f"• {feat}")
                        elif isinstance(features, str):
                            prompt_parts.append(features)
                    
                    # Pricing
                    if biz.get('pricing_info'):
                        prompt_parts.append("\nPRICING:")
                        prompt_parts.append(biz['pricing_info'])
                    
                    # Target customers
                    if biz.get('target_customers'):
                        prompt_parts.append("\nTARGET CUSTOMERS:")
                        prompt_parts.append(biz['target_customers'])
                
                # Add knowledge files
                if agent_obj.knowledge_files and isinstance(agent_obj.knowledge_files, dict):
                    for key, value in agent_obj.knowledge_files.items():
                        if value:
                            prompt_parts.append(f"\n{key.upper().replace('_', ' ')}:")
                            prompt_parts.append(str(value))
            
            # 🔥 INTELLIGENT QUESTION HANDLING
            prompt_parts.append("\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            prompt_parts.append("INTELLIGENT QUESTION HANDLING:")
            prompt_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            prompt_parts.append("\nWHEN CUSTOMER ASKS QUESTIONS:")
            prompt_parts.append("1. Search knowledge base above for relevant information")
            prompt_parts.append("2. Answer in 1-2 sentences maximum")
            prompt_parts.append("3. After answering, RETURN to script where you left off")
            prompt_parts.append("\nEXAMPLES:")
            prompt_parts.append(f'• "Can you hear me?" → "Yes, I can hear you perfectly. Let me continue..."')
            prompt_parts.append(f'• "How are you?" → "I\'m great, thanks! Let me tell you about {company_name}..."')
            prompt_parts.append(f'• Technical question → Answer from knowledge base + continue script')
            prompt_parts.append(f'• Off-topic → "Let me connect you with someone for that. Now, about {company_name}..."')
            prompt_parts.append("\nGOLDEN RULE: Always bring conversation back to sales call after answering questions!")
            
            # 🔥 CRITICAL RULES
            prompt_parts.append("\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            prompt_parts.append("CRITICAL RESPONSE RULES:")
            prompt_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            prompt_parts.append("\n1. Maximum 2 sentences per response - NO EXCEPTIONS")
            prompt_parts.append("2. Use exact script wording for main call flow")
            prompt_parts.append("3. For questions: Search knowledge base → Answer briefly → Return to script")
            prompt_parts.append("4. No filler words: 'um', 'uh', 'like', 'you know', 'hmm', 'well'")
            prompt_parts.append("5. Be direct and professional")
            prompt_parts.append(f"6. Answer ANY question about {company_name} using knowledge base")
            prompt_parts.append("7. For unrelated questions: Brief answer → Redirect to sales call")
            prompt_parts.append("8. Never make up information not in knowledge base")
            prompt_parts.append("9. Always return to script after answering questions")
            prompt_parts.append("10. Keep moving toward demo booking goal")
            prompt_parts.append("\nFORBIDDEN BEHAVIORS:")
            prompt_parts.append("❌ Long responses (>2 sentences)")
            prompt_parts.append("❌ Completely ignoring customer questions")
            prompt_parts.append("❌ Saying 'I don't know' when info is in knowledge base")
            prompt_parts.append("❌ Changing script wording")
            prompt_parts.append("❌ Uncertain phrases ('I think', 'maybe', 'probably')")
            prompt_parts.append("❌ Getting stuck on off-topic discussion")
            prompt_parts.append("❌ Forgetting to return to script after answering")
            prompt_parts.append("\nTONE: Professional, confident, clear, helpful")
            prompt_parts.append("STYLE: Sales call with intelligent question handling")
            prompt_parts.append("GOAL: Answer questions intelligently, deliver script, book demo")
            
            enhanced_prompt = "\n".join(prompt_parts)
            logger.info(f"✅ Intelligent prompt built: {len(enhanced_prompt)} chars")
            logger.info(f"   📝 Sales script: {'YES' if agent_obj.sales_script_text else 'NO'}")
            logger.info(f"   📚 Knowledge base: {'YES' if (agent_obj.knowledge_files or agent_obj.business_info) else 'NO'}")
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"❌ Error building system prompt: {e}")
            return base_prompt
    
    def update_agent(self,
                     config_id: str,
                     name: Optional[str] = None,
                     system_prompt: Optional[str] = None,
                     voice_name: Optional[str] = None,
                     language: Optional[str] = None) -> bool:
        """
        Update existing agent in HumeAI
        
        Args:
            config_id: HumeAI config ID
            name: New agent name (optional)
            system_prompt: New system prompt (optional)
            voice_name: New voice (optional)
            language: New language (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/evi/configs/{config_id}"
            
            payload = {}
            if name:
                payload['name'] = name
            if system_prompt:
                payload['prompt'] = {'text': system_prompt}
            if voice_name:
                payload['voice'] = {'provider': 'HUME_AI', 'name': voice_name}
            if language:
                payload['language'] = {'code': language}
            
            if not payload:
                logger.warning("⚠️ No updates provided for agent")
                return False
            
            logger.info(f"🔄 Updating HumeAI agent: {config_id}")
            response = requests.patch(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ HumeAI agent updated: {config_id}")
                return True
            else:
                logger.error(f"❌ Failed to update HumeAI agent: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating HumeAI agent: {str(e)}")
            return False
    
    def delete_agent(self, config_id: str) -> bool:
        """
        Delete agent from HumeAI
        
        Args:
            config_id: HumeAI config ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/evi/configs/{config_id}"
            
            logger.info(f"🗑️ Deleting HumeAI agent: {config_id}")
            response = requests.delete(url, headers=self.headers, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ HumeAI agent deleted: {config_id}")
                return True
            else:
                logger.error(f"❌ Failed to delete HumeAI agent: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting HumeAI agent: {str(e)}")
            return False
    
    def get_agent(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent details from HumeAI
        
        Args:
            config_id: HumeAI config ID
            
        Returns:
            Agent data if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/evi/configs/{config_id}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get HumeAI agent: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting HumeAI agent: {str(e)}")
            return None
    
    def list_agents(self) -> list:
        """
        List all agents from HumeAI
        
        Returns:
            List of agents
        """
        try:
            url = f"{self.base_url}/evi/configs"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('configs', [])
            else:
                logger.error(f"❌ Failed to list HumeAI agents: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error listing HumeAI agents: {str(e)}")
            return []


# Global service instance
hume_agent_service = HumeAgentService()
