"""
🔍 Test Knowledge Base - Check if agent can find answers for different question variations
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import LearnedKnowledge

print(f"\n{'='*80}")
print(f"🔍 TESTING KNOWLEDGE BASE VARIATIONS")
print(f"{'='*80}\n")

# Different ways customer might ask about PRICE
price_questions = [
    "How much does it cost?",
    "What's the price?",
    "How much is it?",
    "What's the pricing?",
    "Cost?",
    "Price?",
    "How expensive is it?",
    "What does it cost?",
]

print(f"💰 PRICING QUESTIONS:")
print(f"-" * 80)
for q in price_questions:
    # Search in knowledge base
    results = LearnedKnowledge.objects.filter(question__icontains=q.lower().replace("?", ""))
    if results.exists():
        print(f"✅ '{q}' -> FOUND: {results.first().answer[:50]}...")
    else:
        print(f"❌ '{q}' -> NOT FOUND (will use web search)")

print(f"\n")

# Different ways customer might ask WHAT IT DOES
feature_questions = [
    "What does it do?",
    "What's this about?",
    "Tell me about your product",
    "What exactly does your software do?",
    "Explain your product",
    "What can it do for me?",
]

print(f"🤔 FEATURE QUESTIONS:")
print(f"-" * 80)
for q in feature_questions:
    results = LearnedKnowledge.objects.filter(question__icontains=q.lower().replace("?", ""))
    if results.exists():
        print(f"✅ '{q}' -> FOUND: {results.first().answer[:50]}...")
    else:
        print(f"❌ '{q}' -> NOT FOUND (will use web search)")

print(f"\n")

# Different ways customer might ask about SMALL BUSINESS
small_biz_questions = [
    "Is it for small businesses?",
    "Can small companies use this?",
    "Is it suitable for small businesses?",
    "Good for startups?",
    "Works for small teams?",
]

print(f"🏢 SMALL BUSINESS QUESTIONS:")
print(f"-" * 80)
for q in small_biz_questions:
    results = LearnedKnowledge.objects.filter(question__icontains=q.lower().replace("?", ""))
    if results.exists():
        print(f"✅ '{q}' -> FOUND: {results.first().answer[:50]}...")
    else:
        print(f"❌ '{q}' -> NOT FOUND (will use web search)")

print(f"\n{'='*80}")
print(f"📊 SUMMARY")
print(f"{'='*80}")

total_kb = LearnedKnowledge.objects.count()
print(f"Total Q&A pairs in knowledge base: {total_kb}")
print(f"\n💡 HOW IT WORKS:")
print(f"✅ If question matches knowledge base -> Quick answer")
print(f"🌐 If not found -> Web search + Save for next time")
print(f"🧠 Every call -> Learns new Q&A pairs automatically")
print(f"\n{'='*80}\n")
