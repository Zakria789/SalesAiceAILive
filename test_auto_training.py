"""
Test Auto-Training Integration
Verify that ChromaDB learns from calls
"""

import chromadb
from sentence_transformers import SentenceTransformer
import json

def check_learned_knowledge():
    """Check what agent has learned from calls"""
    try:
        print("\n" + "="*60)
        print("🎓 CHECKING AUTO-LEARNED KNOWLEDGE")
        print("="*60)
        
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path="./agent_knowledge_db")
        
        # Get learned conversations collection
        try:
            collection = client.get_collection("learned_conversations")
            count = collection.count()
            
            print(f"\n✅ ChromaDB connected!")
            print(f"📊 Total learned Q&A pairs: {count}")
            
            if count > 0:
                # Get all items
                results = collection.get()
                
                print(f"\n📝 Learned Conversations:")
                print("-" * 60)
                
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    print(f"\n{i+1}. Question: {doc}")
                    print(f"   Answer: {metadata.get('answer', 'N/A')[:100]}...")
                    print(f"   Call SID: {metadata.get('call_sid', 'N/A')}")
                    print(f"   Source: {metadata.get('source', 'N/A')}")
                    
                print("\n" + "="*60)
                
                # Test query
                print("\n🔍 Testing Knowledge Query:")
                print("-" * 60)
                
                model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                
                test_questions = [
                    "How much does it cost?",
                    "What's the price?",
                    "Do you have free trial?",
                    "Can I cancel anytime?"
                ]
                
                for question in test_questions:
                    print(f"\n❓ Question: '{question}'")
                    
                    # Search in learned knowledge
                    embedding = model.encode(question).tolist()
                    search_results = collection.query(
                        query_embeddings=[embedding],
                        n_results=1
                    )
                    
                    if search_results['documents'] and len(search_results['documents'][0]) > 0:
                        matched_q = search_results['documents'][0][0]
                        matched_a = search_results['metadatas'][0][0].get('answer', 'N/A')
                        distance = search_results['distances'][0][0]
                        
                        print(f"✅ Found match! (distance: {distance:.3f})")
                        print(f"   Matched Q: '{matched_q}'")
                        print(f"   Answer: '{matched_a[:100]}...'")
                    else:
                        print(f"❌ No match found")
                
            else:
                print("\n⚠️  No learned conversations yet!")
                print("   Make some test calls to see auto-training in action.")
                
        except Exception as e:
            print(f"\n⚠️  Collection 'learned_conversations' not found")
            print(f"   This is normal if no calls have been made yet")
            print(f"   Error: {e}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def check_other_collections():
    """Check other training collections"""
    try:
        print("\n" + "="*60)
        print("📚 OTHER KNOWLEDGE COLLECTIONS")
        print("="*60)
        
        client = chromadb.PersistentClient(path="./agent_knowledge_db")
        
        # Check agent_knowledge collection
        try:
            knowledge_collection = client.get_collection("agent_knowledge")
            knowledge_count = knowledge_collection.count()
            print(f"\n📖 agent_knowledge: {knowledge_count} items")
            
            if knowledge_count > 0:
                results = knowledge_collection.get(limit=5)
                print(f"   Sample items:")
                for i, (doc, metadata) in enumerate(zip(results['documents'][:3], results['metadatas'][:3])):
                    print(f"   {i+1}. {doc[:80]}...")
                    print(f"      Category: {metadata.get('category', 'N/A')}")
                    
        except Exception as e:
            print(f"\n📖 agent_knowledge: Not found (Error: {e})")
        
        # Check salesaice_knowledge collection
        try:
            salesaice_collection = client.get_collection("salesaice_knowledge")
            salesaice_count = salesaice_collection.count()
            print(f"\n💼 salesaice_knowledge: {salesaice_count} items")
            
        except Exception as e:
            print(f"\n💼 salesaice_knowledge: Not found (Error: {e})")
            
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error checking other collections: {str(e)}")

def show_training_flow():
    """Show how auto-training works"""
    print("\n" + "="*60)
    print("🎯 HOW AUTO-TRAINING WORKS")
    print("="*60)
    
    flow = """
    
1. DURING CALL:
   Customer: "How much does it cost?"
   Agent: "We have three plans: Basic $29, Pro $79, Enterprise $199"
   
   → System stores in conversation_history[]

2. CALL ENDS:
   disconnect() is called
   → auto_train_from_call() runs automatically
   
3. TRAINING:
   - Generate embedding for question
   - Store Q&A pair in ChromaDB
   - Log success
   
4. NEXT CALL:
   New Customer: "What's your pricing?"
   → Search ChromaDB (200ms)
   → Return learned answer
   → Fast response!

✅ Agent gets smarter with EVERY call!
    """
    
    print(flow)

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" AUTO-TRAINING INTEGRATION TEST")
    print("="*70)
    
    # Show how it works
    show_training_flow()
    
    # Check learned knowledge
    check_learned_knowledge()
    
    # Check other collections
    check_other_collections()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
    
    print("\n💡 TIPS:")
    print("   1. Make test calls to see auto-training in action")
    print("   2. Check Daphne logs for training messages")
    print("   3. Run this script after calls to see learned knowledge")
    print("   4. Use /api/agent/training-stats/ to see metrics\n")
