#!/usr/bin/env python3
"""
Asynchronous example of using ColBERT Client SDK.
"""

import asyncio
from re_client import ReServerClient


async def main():
    # Create client
    client = ReServerClient(host="localhost", port=50051)
    
    # Test data
    queries = [
        "machine learning frameworks",
        "web development tools",
        "database management systems"
    ]
    
    documents = [
        "TensorFlow is an open source machine learning framework.",
        "PyTorch is a machine learning library based on Torch.",
        "React is a JavaScript library for building user interfaces.",
        "Django is a high-level Python web framework.",
        "PostgreSQL is a powerful, open source object-relational database.",
        "MongoDB is a document-oriented NoSQL database.",
        "Cooking recipes for Italian pasta.",
        "The weather forecast for tomorrow.",
    ]
    
    print("🚀 Running async reranking for multiple queries...\n")
    
    # Process multiple queries concurrently
    tasks = []
    for query in queries:
        task = client.rerank_async(query, documents)
        tasks.append(task)
    
    try:
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)
        
        # Display results for each query
        for i, (query, response) in enumerate(zip(queries, responses)):
            print(f"📋 Query {i+1}: '{query}'")
            print("Top 3 results:")
            
            for j, result in enumerate(response.top_k(3)):
                print(f"  {j+1}. {result.text} (score: {result.score:.4f})")
            
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def health_check_example():
    """Example of async health check."""
    client = ReServerClient()
    
    print("🏥 Checking server health...")
    
    try:
        is_healthy = await client.health_check_async(timeout=5.0)
        if is_healthy:
            print("✅ Server is healthy!")
        else:
            print("❌ Server is not responding")
    except Exception as e:
        print(f"❌ Health check failed: {e}")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())
    
    # Run health check example
    print("\n" + "="*50 + "\n")
    asyncio.run(health_check_example())
