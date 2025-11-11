"""
Knowledge Manager - Works on Local & PythonAnywhere
Hybrid: ChromaDB (local) + SQLite (production)
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeManager:
    """
    Smart knowledge manager that works everywhere:
    - Local development: Uses ChromaDB (fast, vector search)
    - PythonAnywhere: Uses Django database (reliable, no file issues)
    """
    
    def __init__(self):
        self.backend = self._detect_backend()
        logger.info(f"🧠 Knowledge Manager initialized with backend: {self.backend}")
        
        if self.backend == "chromadb":
            self._init_chromadb()
        else:
            self._init_django_db()
    
    def _detect_backend(self) -> str:
        """
        Auto-detect best backend:
        - PythonAnywhere: Use Django DB
        - Local: Use ChromaDB
        """
        # Check if running on PythonAnywhere
        if os.environ.get('PYTHONANYWHERE_SITE'):
            return "django_db"
        
        # Check if ChromaDB is available
        try:
            import chromadb
            return "chromadb"
        except ImportError:
            return "django_db"
    
    def _init_chromadb(self):
        """Initialize ChromaDB for local development"""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            self.chroma_client = chromadb.PersistentClient(path="./agent_knowledge_db")
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("✅ ChromaDB initialized (Local Development)")
            
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB init failed, falling back to Django DB: {e}")
            self.backend = "django_db"
            self._init_django_db()
    
    def _init_django_db(self):
        """Initialize Django database backend"""
        try:
            from HumeAiTwilio.models import LearnedKnowledge
            self.django_model = LearnedKnowledge
            logger.info("✅ Django DB initialized (Production)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Django DB: {e}")
            self.django_model = None
    
    def add_knowledge(self, question: str, answer: str, metadata: Dict = None) -> bool:
        """
        Add Q&A to knowledge base
        Works on both ChromaDB and Django DB
        """
        try:
            if self.backend == "chromadb":
                return self._add_chromadb(question, answer, metadata)
            else:
                return self._add_django_db(question, answer, metadata)
        except Exception as e:
            logger.error(f"❌ Failed to add knowledge: {e}")
            return False
    
    def _add_chromadb(self, question: str, answer: str, metadata: Dict = None) -> bool:
        """Add to ChromaDB with vector embeddings"""
        try:
            collection = self.chroma_client.get_or_create_collection(
                name="learned_conversations",
                metadata={"description": "Auto-learned from calls"}
            )
            
            # Generate embedding
            embedding = self.embedding_model.encode(question).tolist()
            
            # Create unique ID
            import hashlib
            qid = hashlib.md5(question.encode()).hexdigest()[:16]
            
            # Prepare metadata
            meta = {
                "answer": answer,
                "created_at": str(datetime.now()),
                **(metadata or {})
            }
            
            collection.add(
                ids=[qid],
                embeddings=[embedding],
                documents=[question],
                metadatas=[meta]
            )
            
            logger.info(f"✅ ChromaDB: Stored Q: '{question[:50]}...'")
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromaDB add failed: {e}")
            return False
    
    def _add_django_db(self, question: str, answer: str, metadata: Dict = None) -> bool:
        """Add to Django database"""
        try:
            if not self.django_model:
                return False
            
            # Create or update
            obj, created = self.django_model.objects.update_or_create(
                question=question,
                defaults={
                    'answer': answer,
                    'metadata': json.dumps(metadata or {}),
                    'source': metadata.get('source', 'live_call') if metadata else 'live_call'
                }
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"✅ Django DB: {action} Q: '{question[:50]}...'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Django DB add failed: {e}")
            return False
    
    def search_knowledge(self, query: str, limit: int = 3) -> List[Dict]:
        """
        Search knowledge base
        Returns list of matching Q&A pairs
        """
        try:
            if self.backend == "chromadb":
                return self._search_chromadb(query, limit)
            else:
                return self._search_django_db(query, limit)
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def _search_chromadb(self, query: str, limit: int = 3) -> List[Dict]:
        """Search ChromaDB with vector similarity"""
        try:
            collection = self.chroma_client.get_collection("learned_conversations")
            
            # Generate query embedding
            embedding = self.embedding_model.encode(query).tolist()
            
            # Search
            results = collection.query(
                query_embeddings=[embedding],
                n_results=limit
            )
            
            # Format results
            matches = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    matches.append({
                        'question': doc,
                        'answer': results['metadatas'][0][i].get('answer', ''),
                        'distance': results['distances'][0][i],
                        'metadata': results['metadatas'][0][i]
                    })
            
            logger.info(f"🔍 ChromaDB: Found {len(matches)} matches for '{query[:30]}...'")
            return matches
            
        except Exception as e:
            logger.error(f"❌ ChromaDB search failed: {e}")
            return []
    
    def _search_django_db(self, query: str, limit: int = 3) -> List[Dict]:
        """Search Django database with keyword matching"""
        try:
            if not self.django_model:
                return []
            
            # Simple keyword search
            from django.db.models import Q
            
            results = self.django_model.objects.filter(
                Q(question__icontains=query) | Q(answer__icontains=query)
            ).order_by('-created_at')[:limit]
            
            matches = []
            for result in results:
                matches.append({
                    'question': result.question,
                    'answer': result.answer,
                    'metadata': json.loads(result.metadata) if result.metadata else {}
                })
            
            logger.info(f"🔍 Django DB: Found {len(matches)} matches for '{query[:30]}...'")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Django DB search failed: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            if self.backend == "chromadb":
                return self._get_chromadb_stats()
            else:
                return self._get_django_stats()
        except Exception as e:
            logger.error(f"❌ Stats failed: {e}")
            return {"error": str(e)}
    
    def _get_chromadb_stats(self) -> Dict:
        """Get ChromaDB statistics"""
        try:
            collection = self.chroma_client.get_collection("learned_conversations")
            count = collection.count()
            
            return {
                "backend": "ChromaDB",
                "total_items": count,
                "location": "./agent_knowledge_db"
            }
        except Exception as e:
            return {"backend": "ChromaDB", "error": str(e)}
    
    def _get_django_stats(self) -> Dict:
        """Get Django database statistics"""
        try:
            if not self.django_model:
                return {"backend": "Django DB", "error": "Model not initialized"}
            
            count = self.django_model.objects.count()
            
            return {
                "backend": "Django DB",
                "total_items": count,
                "location": "PostgreSQL/MySQL/SQLite"
            }
        except Exception as e:
            return {"backend": "Django DB", "error": str(e)}


# Global singleton instance
_knowledge_manager = None

def get_knowledge_manager() -> KnowledgeManager:
    """Get or create global KnowledgeManager instance"""
    global _knowledge_manager
    if _knowledge_manager is None:
        _knowledge_manager = KnowledgeManager()
    return _knowledge_manager
