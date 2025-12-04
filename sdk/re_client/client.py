"""
Main client class for ReServer Reranker Server.
"""

from typing import List, Optional

import grpc
from grpc import aio

from .exceptions import (
    ReServerClientError,
    ReServerConnectionError,
    ReServerServerError,
    ReServerTimeoutError,
    ReServerValidationError,
)
from .models import RerankResponse, RerankResult
from .reranker_pb2 import RerankRequest as ProtoRerankRequest
from .reranker_pb2_grpc import RerankServiceStub


class ReServerClient:
    """
    Client for ReServer Reranker Server.

    Provides both synchronous and asynchronous interfaces for document reranking.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
        timeout: float = 30.0,
        max_retries: int = 3,
        secure: bool = False,
        credentials: Optional[grpc.ChannelCredentials] = None,
    ):
        """
        Initialize ReServer client.

        Args:
            host: Server hostname
            port: Server port
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            secure: Whether to use secure connection
            credentials: gRPC credentials for secure connections
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.secure = secure
        self.credentials = credentials
        self._address = f"{host}:{port}"

    def _create_channel(self) -> grpc.Channel:
        """Create a gRPC channel."""
        if self.secure:
            if self.credentials:
                return grpc.secure_channel(self._address, self.credentials)
            else:
                return grpc.secure_channel(
                    self._address, grpc.ssl_channel_credentials()
                )
        else:
            return grpc.insecure_channel(self._address)

    def _create_async_channel(self) -> aio.Channel:
        """Create an async gRPC channel."""
        if self.secure:
            if self.credentials:
                return aio.secure_channel(self._address, self.credentials)
            else:
                return aio.secure_channel(self._address, grpc.ssl_channel_credentials())
        else:
            return aio.insecure_channel(self._address)

    def _validate_request(self, query: str, documents: List[str]) -> None:
        """Validate rerank request parameters."""
        if not query or not query.strip():
            raise ReServerValidationError("Query cannot be empty")

        if not documents:
            raise ReServerValidationError("Documents list cannot be empty")

        if len(documents) > 1000:  # Reasonable limit
            raise ReServerValidationError("Too many documents (max 1000)")

        for i, doc in enumerate(documents):
            if not doc or not doc.strip():
                raise ReServerValidationError(f"Document at index {i} cannot be empty")

    def _convert_response(self, proto_response) -> RerankResponse:
        """Convert protobuf response to SDK response."""
        results = []
        for proto_result in proto_response.results:
            result = RerankResult(
                original_index=proto_result.original_index,
                score=proto_result.score,
                text=proto_result.text,
            )
            results.append(result)

        return RerankResponse(results=results)

    def rerank(
        self,
        query: str,
        documents: List[str],
        timeout: Optional[float] = None,
    ) -> RerankResponse:
        """
        Rerank documents based on query relevance (synchronous).

        Args:
            query: Search query
            documents: List of documents to rerank
            timeout: Request timeout (overrides default)

        Returns:
            RerankResponse with ranked results

        Raises:
            ReServerValidationError: Invalid input parameters
            ReServerConnectionError: Connection failed
            ReServerServerError: Server error
            ReServerTimeoutError: Request timeout
        """
        self._validate_request(query, documents)

        request_timeout = timeout or self.timeout

        try:
            with self._create_channel() as channel:
                stub = RerankServiceStub(channel)

                proto_request = ProtoRerankRequest(query=query, documents=documents)

                proto_response = stub.Rerank(proto_request, timeout=request_timeout)

                return self._convert_response(proto_response)

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ReServerConnectionError(
                    f"Cannot connect to server at {self._address}"
                )
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise ReServerTimeoutError(
                    f"Request timed out after {request_timeout}s"
                )
            else:
                raise ReServerServerError(f"Server error: {e.details()}", str(e.code()))
        except Exception as e:
            raise ReServerClientError(f"Unexpected error: {str(e)}")

    async def rerank_async(
        self,
        query: str,
        documents: List[str],
        timeout: Optional[float] = None,
    ) -> RerankResponse:
        """
        Rerank documents based on query relevance (asynchronous).

        Args:
            query: Search query
            documents: List of documents to rerank
            timeout: Request timeout (overrides default)

        Returns:
            RerankResponse with ranked results

        Raises:
            ReServerValidationError: Invalid input parameters
            ReServerConnectionError: Connection failed
            ReServerServerError: Server error
            ReServerTimeoutError: Request timeout
        """
        self._validate_request(query, documents)

        request_timeout = timeout or self.timeout

        try:
            async with self._create_async_channel() as channel:
                stub = RerankServiceStub(channel)

                proto_request = ProtoRerankRequest(query=query, documents=documents)

                proto_response = await stub.Rerank(
                    proto_request, timeout=request_timeout
                )

                return self._convert_response(proto_response)

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ConnectionError(f"Cannot connect to server at {self._address}")
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise ReServerTimeoutError(
                    f"Request timed out after {request_timeout}s"
                )
            else:
                raise ReServerServerError(f"Server error: {e.details()}", str(e.code()))
        except Exception as e:
            raise ReServerClientError(f"Unexpected error: {str(e)}")

    def health_check(self, timeout: Optional[float] = None) -> bool:
        """
        Check if server is healthy.

        Args:
            timeout: Request timeout

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Simple health check by sending a minimal request
            self.rerank("test", ["test document"], timeout=timeout or 5.0)
            return True
        except Exception:
            return False

    async def health_check_async(self, timeout: Optional[float] = None) -> bool:
        """
        Check if server is healthy (asynchronous).

        Args:
            timeout: Request timeout

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Simple health check by sending a minimal request
            await self.rerank_async("test", ["test document"], timeout=timeout or 5.0)
            return True
        except Exception:
            return False
