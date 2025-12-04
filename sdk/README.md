# ReServer Client SDK

A Python SDK for interacting with the Reranker Server via gRPC. This library provides both synchronous and asynchronous interfaces for document reranking with comprehensive error handling and utility functions.

## Installation

```bash
pip install reserver-client
```

Or install from source:

```bash
cd sdk
uv sync
uv build
pip install dist/*.whl
```

## Quick Start

### Basic Usage

```python
from re_client import ReServerClient

# Create client
client = ReServerClient(host="localhost", port=50051)

# Rerank documents
response = client.rerank(
    query="machine learning frameworks",
    documents=[
        "TensorFlow is a machine learning library",
        "React is a web development framework",
        "PyTorch is used for deep learning"
    ]
)

# Process results
for result in response.results:
    print(f"Score: {result.score:.4f} - {result.text}")
```

### Async Usage

```python
import asyncio
from re_client import ReServerClient

async def main():
    client = ReServerClient()

    response = await client.rerank_async(
        query="python package managers",
        documents=[
            "pip is the standard Python package installer",
            "uv is a fast Python package manager written in Rust",
            "npm is a package manager for JavaScript"
        ]
    )

    for result in response.top_k(2):
        print(f"{result.text} (score: {result.score:.4f})")

asyncio.run(main())
```

## Configuration

### Environment Variables

The SDK can be configured using environment variables:

```bash
export RESERVER_HOST=localhost
export RESERVER_PORT=50051
export RESERVER_TIMEOUT=30.0
export RESERVER_MAX_RETRIES=3
export RESERVER_SECURE=false
```

### Programmatic Configuration

```python
from re_client import ReServerClient, ClientConfig

# Using ClientConfig
config = ClientConfig(
    host="production-server.com",
    port=443,
    timeout=60.0,
    max_retries=5,
    secure=True
)

client = ReServerClient(
    host=config.host,
    port=config.port,
    timeout=config.timeout,
    max_retries=config.max_retries,
    secure=config.secure
)

# Or from environment
config = ClientConfig.from_env()
client = ReServerClient(**config.__dict__)
```

## Advanced Features

### Batch Processing

For processing multiple queries or large document sets:

```python
from re_client.utils import batch_rerank

results = batch_rerank(
    client=client,
    queries=["query1", "query2"],
    documents_list=[["doc1", "doc2"], ["doc3", "doc4"]],
    batch_size=10,
    max_workers=4
)
```

### Filtering and Utilities

```python
from re_client.utils import (
    filter_by_score_threshold,
    get_top_k_with_threshold,
    calculate_score_statistics
)

# Filter by minimum score
filtered_results = filter_by_score_threshold(
    response.results,
    threshold=0.5
)

# Get top k results above threshold
top_results = get_top_k_with_threshold(
    response.results,
    k=5,
    threshold=0.3
)

# Calculate statistics
stats = calculate_score_statistics(response.results)
print(f"Mean: {stats['mean']:.4f}")
print(f"Std: {stats['std']:.4f}")
```

### Error Handling

```python
from re_client import (
    ReServerClientError,      # Base exception
    ReServerConnectionError,  # Connection issues
    ReServerTimeoutError,     # Request timeouts
    ReServerServerError,      # Server-side errors
    ReServerValidationError   # Input validation errors
)

try:
    response = client.rerank(query, documents)
except ReServerConnectionError:
    print("Cannot connect to server")
except ReServerTimeoutError:
    print("Request timed out")
except ReServerValidationError as e:
    print(f"Invalid input: {e}")
except ReServerServerError as e:
    print(f"Server error: {e}")
except ReServerClientError as e:
    print(f"Client error: {e}")
```

### Health Check

```python
# Synchronous health check
if client.health_check():
    print("Server is healthy")

# Asynchronous health check
if await client.health_check_async():
    print("Server is healthy")
```

## API Reference

### ReServerClient

The main client class for interacting with the reranking server.

#### Constructor

```python
ReServerClient(
    host: str = "localhost",
    port: int = 50051,
    timeout: float = 30.0,
    max_retries: int = 3,
    secure: bool = False,
    credentials: Optional[grpc.ChannelCredentials] = None
)
```

**Parameters:**
- `host`: Server hostname
- `port`: Server port
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum number of retry attempts
- `secure`: Whether to use secure connection (TLS)
- `credentials`: gRPC credentials for secure connections

#### Methods

##### rerank()

Synchronous document reranking.

```python
def rerank(
    self,
    query: str,
    documents: List[str],
    timeout: Optional[float] = None
) -> RerankResponse
```

**Parameters:**
- `query`: Search query string
- `documents`: List of documents to rerank
- `timeout`: Optional request timeout override

**Returns:** `RerankResponse` object with ranked results

**Raises:**
- `ReServerValidationError`: Invalid input parameters
- `ReServerConnectionError`: Cannot connect to server
- `ReServerTimeoutError`: Request timeout
- `ReServerServerError`: Server-side error
- `ReServerClientError`: Unexpected client error

##### rerank_async()

Asynchronous document reranking.

```python
async def rerank_async(
    self,
    query: str,
    documents: List[str],
    timeout: Optional[float] = None
) -> RerankResponse
```

Same parameters and return type as `rerank()`, but returns a coroutine.

##### health_check()

Check server health synchronously.

```python
def health_check(self, timeout: Optional[float] = None) -> bool
```

**Returns:** `True` if server is healthy, `False` otherwise

##### health_check_async()

Check server health asynchronously.

```python
async def health_check_async(self, timeout: Optional[float] = None) -> bool
```

### Data Models

#### RerankResponse

Container for reranking results.

```python
@dataclass
class RerankResponse:
    results: List[RerankResult]

    def __len__(self) -> int
    def __iter__(self)
    def __getitem__(self, index: int) -> RerankResult
    def top_k(self, k: int) -> List[RerankResult]
    def get_by_original_index(self, original_index: int) -> Optional[RerankResult]
```

**Methods:**
- `top_k(k)`: Get top k results
- `get_by_original_index(index)`: Get result by original document index

#### RerankResult

Individual reranking result.

```python
@dataclass
class RerankResult:
    original_index: int  # Original position in input documents
    score: float         # Relevance score
    text: str           # Document text
```

#### RerankRequest

Request model for validation.

```python
@dataclass
class RerankRequest:
    query: str
    documents: List[str]
```

Automatically validates that query and documents are not empty.

### Utility Functions

#### batch_rerank()

Process multiple queries in batches.

```python
from re_client.utils import batch_rerank

results = batch_rerank(
    client=client,
    queries=["query1", "query2"],
    documents_list=[["doc1", "doc2"], ["doc3", "doc4"]],
    batch_size=10,
    max_workers=4
)
```

#### filter_by_score_threshold()

Filter results by minimum score.

```python
from re_client.utils import filter_by_score_threshold

filtered_results = filter_by_score_threshold(
    response.results,
    threshold=0.5
)
```

#### get_top_k_with_threshold()

Get top k results above threshold.

```python
from re_client.utils import get_top_k_with_threshold

top_results = get_top_k_with_threshold(
    response.results,
    k=5,
    threshold=0.3
)
```

#### calculate_score_statistics()

Calculate score statistics.

```python
from re_client.utils import calculate_score_statistics

stats = calculate_score_statistics(response.results)
print(f"Mean: {stats['mean']:.4f}")
print(f"Std: {stats['std']:.4f}")
print(f"Min: {stats['min']:.4f}")
print(f"Max: {stats['max']:.4f}")
```

#### retry_on_failure()

Decorator for automatic retry logic.

```python
from re_client.utils import retry_on_failure

@retry_on_failure(max_retries=3, delay=1.0)
def my_rerank_function():
    return client.rerank(query, documents)
```

## Examples

The `examples/` directory contains complete usage examples:

- `basic_example.py` - Basic synchronous usage
- `async_example.py` - Asynchronous usage and health checks

### Basic Example

```python
#!/usr/bin/env python3
from re_client import ReServerClient

def main():
    client = ReServerClient(host="localhost", port=50051)

    query = "how to install python dependencies fast"
    documents = [
        "The sky is blue and the day is beautiful.",
        "UV is an extremely fast Python package manager written in Rust.",
        "Carrot cake recipe with chocolate.",
        "Pip is the standard installer for Python packages.",
        "The history of the Roman Empire.",
    ]

    try:
        response = client.rerank(query, documents)

        print(f"Query: '{query}'")
        print(f"Reranking {len(documents)} documents...")
        print()

        for i, result in enumerate(response.results):
            print(f"{i+1}. {result.text}")
            print(f"   Score: {result.score:.4f}, Original Index: {result.original_index}")
            print()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

## Requirements

- Python 3.8+
- grpcio >= 1.50.0
- protobuf >= 4.0.0

## Development

### Building from Source

```bash
cd sdk
uv sync --dev
uv build
```

### Running Tests

```bash
cd sdk
uv run pytest
```

### Code Quality

```bash
cd sdk
uv run black .
uv run isort .
uv run mypy .
```

## License

MIT License
