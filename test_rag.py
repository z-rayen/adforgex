from rag.rag_engine import RAGEngine

engine = RAGEngine()
engine.initialize()

print(f"Total documents in RAG: {engine.count()}")
print("\nSearching for 'fashion spring collection new arrivals'...\n")

results = engine.search("fashion spring collection new arrivals", top_k=5)

for i, result in enumerate(results, 1):
    print(f"{i}. Category: {result.get('category', 'N/A')}")
    print(f"   Hook: {result.get('hook', 'N/A')[:80]}...")
    print(f"   Similarity Score: {result.get('similarity_score', 0):.3f}")
    print(f"   Performance: {result.get('performance_score', 0)}")
    print()

print(f"\n✓ Successfully retrieved {len(results)} relevant patterns!")
