"""
Data models for Reranker Client SDK.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RerankResult:
    """Represents a single reranking result."""
    
    original_index: int
    score: float
    text: str
    
    def __str__(self) -> str:
        return f"RerankResult(index={self.original_index}, score={self.score:.4f}, text='{self.text[:50]}...')"


@dataclass
class RerankRequest:
    """Represents a reranking request."""
    
    query: str
    documents: List[str]
    
    def __post_init__(self):
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        if not self.documents:
            raise ValueError("Documents list cannot be empty")
        if any(not doc.strip() for doc in self.documents):
            raise ValueError("Documents cannot contain empty strings")


@dataclass
class RerankResponse:
    """Represents a reranking response."""
    
    results: List[RerankResult]
    
    def __len__(self) -> int:
        return len(self.results)
    
    def __iter__(self):
        return iter(self.results)
    
    def __getitem__(self, index: int) -> RerankResult:
        return self.results[index]
    
    def top_k(self, k: int) -> List[RerankResult]:
        """Get top k results."""
        return self.results[:k]
    
    def get_by_original_index(self, original_index: int) -> Optional[RerankResult]:
        """Get result by original document index."""
        for result in self.results:
            if result.original_index == original_index:
                return result
        return None
