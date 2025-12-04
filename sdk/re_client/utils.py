"""
Utility functions for ReServer Client SDK.
"""

import time
from functools import wraps
from typing import Callable, List, Optional

from .exceptions import ReServerClientError
from .models import RerankResponse, RerankResult


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (ReServerClientError,),
):
    """
    Decorator to retry function calls on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        raise last_exception

            return None  # Should never reach here

        return wrapper

    return decorator


def batch_rerank(
    client,
    query: str,
    documents: List[str],
    batch_size: int = 100,
    timeout: Optional[float] = None,
) -> RerankResponse:
    """
    Rerank documents in batches for large document sets.

    Args:
        client: ReServerClient instance
        query: Search query
        documents: List of documents to rerank
        batch_size: Number of documents per batch
        timeout: Request timeout per batch

    Returns:
        Combined RerankResponse with all results
    """
    if len(documents) <= batch_size:
        return client.rerank(query, documents, timeout=timeout)

    all_results = []

    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i : i + batch_size]
        batch_response = client.rerank(query, batch_docs, timeout=timeout)

        # Adjust original indices to account for batching
        for result in batch_response.results:
            adjusted_result = RerankResult(
                original_index=result.original_index + i,
                score=result.score,
                text=result.text,
            )
            all_results.append(adjusted_result)

    # Sort all results by score
    all_results.sort(key=lambda x: x.score, reverse=True)

    return RerankResponse(results=all_results)


def filter_by_score_threshold(
    response: RerankResponse, threshold: float
) -> RerankResponse:
    """
    Filter results by minimum score threshold.

    Args:
        response: Original rerank response
        threshold: Minimum score threshold

    Returns:
        Filtered RerankResponse
    """
    filtered_results = [
        result for result in response.results if result.score >= threshold
    ]

    return RerankResponse(results=filtered_results)


def get_top_k_with_threshold(
    response: RerankResponse, k: int, threshold: Optional[float] = None
) -> RerankResponse:
    """
    Get top k results, optionally filtered by score threshold.

    Args:
        response: Original rerank response
        k: Number of top results to return
        threshold: Optional minimum score threshold

    Returns:
        Filtered RerankResponse with top k results
    """
    results = response.results

    if threshold is not None:
        results = [r for r in results if r.score >= threshold]

    top_k_results = results[:k]

    return RerankResponse(results=top_k_results)


def calculate_score_statistics(response: RerankResponse) -> dict:
    """
    Calculate basic statistics for reranking scores.

    Args:
        response: Rerank response

    Returns:
        Dictionary with score statistics
    """
    if not response.results:
        return {
            "count": 0,
            "min_score": 0.0,
            "max_score": 0.0,
            "mean_score": 0.0,
            "median_score": 0.0,
        }

    scores = [result.score for result in response.results]
    scores.sort()

    count = len(scores)
    min_score = scores[0]
    max_score = scores[-1]
    mean_score = sum(scores) / count

    # Calculate median
    if count % 2 == 0:
        median_score = (scores[count // 2 - 1] + scores[count // 2]) / 2
    else:
        median_score = scores[count // 2]

    return {
        "count": count,
        "min_score": min_score,
        "max_score": max_score,
        "mean_score": mean_score,
        "median_score": median_score,
    }
