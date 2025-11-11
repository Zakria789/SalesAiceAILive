"""
🎯 CONTINUOUS LEARNING API SYSTEM
==================================

Auto-trains agent from:
1. Every call (conversation logs)
2. PDF/Word documents
3. Sales scripts
4. Customer interactions

Features:
✅ Extract knowledge from calls
✅ Upload & process documents
✅ Auto-update knowledge base
✅ Train from sales scripts
✅ Learn from successful conversations
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import PyPDF2
import docx
import re
import logging

# Module logger
logger = logging.getLogger(__name__)

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./agent_knowledge_db")

# Initialize an embedding function with graceful fallback.
# Loading sentence-transformers can fail on low-memory machines (OSError related to paging file).
# Strategy:
# 1. Try to load a local SentenceTransformer embedding.
# 2. If it fails, and OPENAI_API_KEY is set, fall back to OpenAI embeddings.
# 3. Otherwise, create/get collections without an embedding function (use existing collections as-is).
sentence_transformer_ef = None
openai_ef = None

try:
    try:
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info("✅ Loaded SentenceTransformer embedding function")
    except Exception as e:
        # Likely an OSError due to insufficient virtual memory/paging file when loading weights
        logger.warning(f"⚠️ Failed to load SentenceTransformer embedding: {e}")

    # If sentence transformer couldn't be loaded, try OpenAI (if API key available)
    if sentence_transformer_ef is None:
        try:
            from decouple import config as _config
            openai_key = _config('OPENAI_API_KEY', default='')
            if openai_key:
                openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=openai_key)
                logger.info("✅ Falling back to OpenAI embedding function")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI embedding fallback failed: {e}")

except Exception as e:
    # Catch-all - ensure module import doesn't crash the whole Django process
    logger.error(f"❌ Unexpected error initializing embedding functions: {e}")
    sentence_transformer_ef = None
    openai_ef = None

# Helper to create/get collection depending on which embedding function is available
def _get_or_create_collection(name: str):
    # Prefer existing collection (so we don't override embedding config)
    try:
        return client.get_collection(name=name)
    except Exception:
        # Create collection with the best available embedding function
        ef = sentence_transformer_ef or openai_ef
        if ef is not None:
            return client.create_collection(name=name, embedding_function=ef)
        else:
            # Create without embedding function; user can embed later or rely on persisted collection
            return client.create_collection(name=name)

# Get or create collections
knowledge_collection = _get_or_create_collection("agent_knowledge")
conversation_collection = _get_or_create_collection("learned_conversations")


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def extract_qa_from_conversation(conversation: List[Dict]) -> List[Dict]:
    """Extract Q&A pairs from conversation"""
    qa_pairs = []
    
    for i in range(len(conversation) - 1):
        if conversation[i]['role'] == 'user':
            user_msg = conversation[i]['text']
            
            # Find next agent response
            for j in range(i + 1, len(conversation)):
                if conversation[j]['role'] == 'agent':
                    agent_msg = conversation[j]['text']
                    
                    qa_pairs.append({
                        'question': user_msg,
                        'answer': agent_msg,
                        'timestamp': conversation[j].get('timestamp', datetime.now().isoformat())
                    })
                    break
    
    return qa_pairs


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from Word document"""
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks for embedding"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks


def extract_key_phrases(text: str) -> List[str]:
    """Extract key phrases from text"""
    # Simple keyword extraction (can be enhanced with NLP)
    patterns = [
        r"pricing is \$[\d,]+",
        r"features include .{1,100}",
        r"we offer .{1,100}",
        r"benefits are .{1,100}",
    ]
    
    key_phrases = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        key_phrases.extend(matches)
    
    return key_phrases


# ═══════════════════════════════════════════════════════════
# API 1: TRAIN FROM CALL
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def train_from_call(request):
    """
    Train agent from completed call
    
    POST /api/agent/train-from-call/
    
    Body:
    {
        "call_sid": "CAxxxx",
        "conversation": [
            {"role": "agent", "text": "Hello...", "timestamp": "..."},
            {"role": "user", "text": "Hi...", "timestamp": "..."}
        ],
        "outcome": "successful",  # or "unsuccessful"
        "metadata": {
            "duration": 120,
            "customer_name": "John Doe"
        }
    }
    """
    try:
        data = json.loads(request.body)
        
        call_sid = data.get('call_sid')
        conversation = data.get('conversation', [])
        outcome = data.get('outcome', 'unknown')
        metadata = data.get('metadata', {})
        
        if not conversation:
            return JsonResponse({
                'success': False,
                'error': 'No conversation provided'
            }, status=400)
        
        # Extract Q&A pairs
        qa_pairs = extract_qa_from_conversation(conversation)
        
        if not qa_pairs:
            return JsonResponse({
                'success': False,
                'error': 'No Q&A pairs found in conversation'
            }, status=400)
        
        # Add to knowledge base (only if successful call)
        added_count = 0
        if outcome == 'successful':
            for idx, qa in enumerate(qa_pairs):
                doc_id = f"call_{call_sid}_{idx}"
                
                conversation_collection.add(
                    documents=[qa['question']],
                    metadatas=[{
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'call_sid': call_sid,
                        'outcome': outcome,
                        'learned_at': datetime.now().isoformat(),
                        **metadata
                    }],
                    ids=[doc_id]
                )
                added_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Learned from call {call_sid}',
            'qa_pairs_extracted': len(qa_pairs),
            'qa_pairs_added': added_count,
            'outcome': outcome
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 2: TRAIN FROM DOCUMENT
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def train_from_document(request):
    """
    Train agent from uploaded document (PDF, Word, TXT)
    
    POST /api/agent/train-from-document/
    
    Form Data:
    - file: PDF/Word/TXT file
    - category: "sales_script", "product_info", "faq", etc.
    - title: Document title
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        category = request.POST.get('category', 'general')
        title = request.POST.get('title', uploaded_file.name)
        
        # Save file temporarily
        file_path = default_storage.save(f'temp/{uploaded_file.name}', uploaded_file)
        full_path = default_storage.path(file_path)
        
        # Extract text based on file type
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext == '.pdf':
            text = extract_text_from_pdf(full_path)
        elif file_ext in ['.docx', '.doc']:
            text = extract_text_from_docx(full_path)
        elif file_ext == '.txt':
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported file type: {file_ext}'
            }, status=400)
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=500)
        
        # Add to knowledge base
        doc_ids = []
        for idx, chunk in enumerate(chunks):
            doc_id = f"doc_{title}_{idx}_{datetime.now().timestamp()}"
            doc_ids.append(doc_id)
            
            knowledge_collection.add(
                documents=[chunk],
                metadatas=[{
                    'title': title,
                    'category': category,
                    'chunk_index': idx,
                    'total_chunks': len(chunks),
                    'file_type': file_ext,
                    'uploaded_at': datetime.now().isoformat()
                }],
                ids=[doc_id]
            )
        
        # Clean up temp file
        default_storage.delete(file_path)
        
        return JsonResponse({
            'success': True,
            'message': f'Document "{title}" processed successfully',
            'file_name': uploaded_file.name,
            'file_type': file_ext,
            'category': category,
            'chunks_added': len(chunks),
            'total_characters': len(text)
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 3: TRAIN FROM SALES SCRIPT
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def train_from_sales_script(request):
    """
    Train agent from sales script
    
    POST /api/agent/train-from-sales-script/
    
    Body:
    {
        "script_name": "Cold Call Script v2",
        "sections": {
            "opening": "Hello, this is Sarah from...",
            "value_proposition": "We help businesses...",
            "objection_handling": {
                "price": "I understand budget is important...",
                "timing": "I appreciate that..."
            },
            "closing": "Can I schedule a demo..."
        }
    }
    """
    try:
        data = json.loads(request.body)
        
        script_name = data.get('script_name', 'Unnamed Script')
        sections = data.get('sections', {})
        
        if not sections:
            return JsonResponse({
                'success': False,
                'error': 'No sections provided'
            }, status=400)
        
        # Process each section
        added_count = 0
        for section_name, content in sections.items():
            if isinstance(content, dict):
                # Handle nested sections (like objection_handling)
                for sub_name, sub_content in content.items():
                    doc_id = f"script_{script_name}_{section_name}_{sub_name}_{datetime.now().timestamp()}"
                    
                    knowledge_collection.add(
                        documents=[f"{section_name} - {sub_name}: {sub_content}"],
                        metadatas=[{
                            'script_name': script_name,
                            'section': section_name,
                            'subsection': sub_name,
                            'content': sub_content,
                            'type': 'sales_script',
                            'added_at': datetime.now().isoformat()
                        }],
                        ids=[doc_id]
                    )
                    added_count += 1
            else:
                # Handle flat sections
                doc_id = f"script_{script_name}_{section_name}_{datetime.now().timestamp()}"
                
                knowledge_collection.add(
                    documents=[f"{section_name}: {content}"],
                    metadatas=[{
                        'script_name': script_name,
                        'section': section_name,
                        'content': content,
                        'type': 'sales_script',
                        'added_at': datetime.now().isoformat()
                    }],
                    ids=[doc_id]
                )
                added_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Sales script "{script_name}" added successfully',
            'script_name': script_name,
            'sections_added': added_count
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 4: QUERY KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def query_knowledge(request):
    """
    Query the trained knowledge base
    
    POST /api/agent/query-knowledge/
    
    Body:
    {
        "query": "What is our pricing?",
        "n_results": 3,
        "source": "all"  # or "documents", "conversations", "scripts"
    }
    """
    try:
        data = json.loads(request.body)
        
        query = data.get('query')
        n_results = data.get('n_results', 3)
        source = data.get('source', 'all')
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'No query provided'
            }, status=400)
        
        results = []
        
        # Query knowledge collection
        if source in ['all', 'documents', 'scripts']:
            knowledge_results = knowledge_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            for i, doc in enumerate(knowledge_results['documents'][0]):
                results.append({
                    'source': 'knowledge',
                    'content': doc,
                    'metadata': knowledge_results['metadatas'][0][i],
                    'distance': knowledge_results['distances'][0][i]
                })
        
        # Query conversation collection
        if source in ['all', 'conversations']:
            conv_results = conversation_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            for i, doc in enumerate(conv_results['documents'][0]):
                results.append({
                    'source': 'conversation',
                    'content': doc,
                    'metadata': conv_results['metadatas'][0][i],
                    'distance': conv_results['distances'][0][i]
                })
        
        # Sort by relevance (distance)
        results.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'success': True,
            'query': query,
            'results': results[:n_results],
            'total_found': len(results)
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 5: GET TRAINING STATS
# ═══════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def get_training_stats(request):
    """
    Get training statistics
    
    GET /api/agent/training-stats/
    """
    try:
        knowledge_count = knowledge_collection.count()
        conversation_count = conversation_collection.count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'knowledge_items': knowledge_count,
                'learned_conversations': conversation_count,
                'total_items': knowledge_count + conversation_count,
                'last_updated': datetime.now().isoformat()
            }
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ═══════════════════════════════════════════════════════════
# API 6: AUTO-TRAIN FROM CALL (WEBHOOK)
# ═══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def auto_train_webhook(request):
    """
    Webhook that automatically trains from every completed call
    
    Called by Twilio status callback or internal system
    
    POST /api/agent/auto-train-webhook/
    """
    try:
        data = json.loads(request.body)
        
        call_sid = data.get('call_sid')
        
        # Fetch conversation from database
        from HumeAiTwilio.models import ConversationLog, TwilioCall
        
        call = TwilioCall.objects.filter(call_sid=call_sid).first()
        if not call:
            return JsonResponse({
                'success': False,
                'error': 'Call not found'
            }, status=404)
        
        # Get conversation logs
        logs = ConversationLog.objects.filter(call=call).order_by('timestamp')
        
        conversation = []
        for log in logs:
            conversation.append({
                'role': log.speaker,
                'text': log.message,
                'timestamp': log.timestamp.isoformat()
            })
        
        # Determine outcome based on call duration and status
        outcome = 'successful' if call.duration and call.duration > 60 else 'unsuccessful'
        
        # Train from this call
        qa_pairs = extract_qa_from_conversation(conversation)
        
        added_count = 0
        if outcome == 'successful' and qa_pairs:
            for idx, qa in enumerate(qa_pairs):
                doc_id = f"auto_call_{call_sid}_{idx}"
                
                conversation_collection.add(
                    documents=[qa['question']],
                    metadatas=[{
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'call_sid': call_sid,
                        'outcome': outcome,
                        'auto_learned': True,
                        'learned_at': datetime.now().isoformat()
                    }],
                    ids=[doc_id]
                )
                added_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Auto-trained from call {call_sid}',
            'qa_pairs_added': added_count,
            'outcome': outcome
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
