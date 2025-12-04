"""
ReServer Client SDK

A Python SDK for interacting with ReServer Reranker Server via gRPC.

Example usage:
    from re_client import ReServerClient

    client = ReServerClient(host="localhost", port=50051)

    response = client.rerank(
        query="how to install python dependencies fast",
        documents=[
            "UV is an extremely fast Python package manager written in Rust.",
            "Pip is the standard installer for Python packages.",
            "The sky is blue and the day is beautiful.",
        ]
    )

    for result in response.results:
        print(f"Score: {result.score:.4f} - {result.text}")
"""

from .client import ReServerClient
from .config import ClientConfig, get_default_config
from .exceptions import (
    ReServerClientError,
    ReServerConnectionError,
    ReServerServerError,
    ReServerTimeoutError,
    ReServerValidationError,
)
from .models import RerankRequest, RerankResponse, RerankResult
from .utils import (
    batch_rerank,
    calculate_score_statistics,
    filter_by_score_threshold,
    get_top_k_with_threshold,
    retry_on_failure,
)

__version__ = "0.1.0"
__all__ = [
    # Main client
    "ReServerClient",
    # Configuration
    "ClientConfig",
    "get_default_config",
    # Exceptions
    "ReServerClientError",
    "ReServerConnectionError",
    "ReServerServerError",
    "ReServerTimeoutError",
    "ReServerValidationError",
    # Models
    "RerankRequest",
    "RerankResult",
    "RerankResponse",
    # Utilities
    "batch_rerank",
    "filter_by_score_threshold",
    "get_top_k_with_threshold",
    "calculate_score_statistics",
    "retry_on_failure",
]
