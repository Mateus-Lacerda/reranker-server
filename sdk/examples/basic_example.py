#!/usr/bin/env python3
"""
Basic example of using ColBERT Client SDK.
"""

from re_client import ReServerClient


def main():
    # Create client with default settings
    client = ReServerClient(host="localhost", port=50051)
    
    # Test data
    query = "how to install python dependencies fast"
    
    documents = [
        "The sky is blue and the day is beautiful.",
        "UV is an extremely fast Python package manager written in Rust.",
        "Carrot cake recipe with chocolate.",
        "Pip is the standard installer for Python packages.",
        "The history of the Roman Empire.",
    ]
    
    print(f"🔍 Query: '{query}'")
    print(f"📄 Reranking {len(documents)} documents...\n")
    
    try:
        # Perform reranking
        response = client.rerank(query, documents)
        
        print("✅ Results:\n")
        print(f"{'RANK':<5} | {'SCORE':<10} | {'ORIGINAL INDEX':<15} | {'TEXT'}")
        print("-" * 80)
        
        # Display results
        for i, result in enumerate(response.results):
            print(
                f"{i + 1:<5} | {result.score:.4f}     | {result.original_index:<15} | {result.text}"
            )
        
        print(f"\n📊 Total results: {len(response)}")
        
        # Show top 3 results
        print("\n🏆 Top 3 results:")
        for i, result in enumerate(response.top_k(3)):
            print(f"  {i+1}. {result.text} (score: {result.score:.4f})")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
