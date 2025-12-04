# Reranker Server Client SDK

A Python SDK for interacting with the Reranker Server via gRPC.

## Installation

```bash
pip install re-client
```

Or install from source:

```bash
cd sdk
pip install .
```

## Quick Start

### Basic Usage

```python
from re_client import ColBERTClient

# Create client
client = ColBERTClient(host="localhost", port=50051)

# Rerank documents
response = client.rerank(
    query="how to install python dependencies fast",
    documents=[
        "UV is an extremely fast Python package manager written in Rust.",
        "Pip is the standard installer for Python packages.",
        "The sky is blue and the day is beautiful.",
    ]
)

# Print results
for i, result in enumerate(response.results):
    print(f"{i+1}. Score: {result.score:.4f} - {result.text}")
```

### Async Usage

```python
import asyncio
from re_client import ColBERTClient

async def main():
    client = ColBERTClient()
    
    response = await client.rerank_async(
        query="machine learning frameworks",
        documents=[
            "TensorFlow is an open source machine learning framework.",
            "PyTorch is a machine learning library based on Torch.",
            "Cooking recipes for Italian pasta.",
        ]
    )
    
    for result in response.top_k(2):
        print(f"Score: {result.score:.4f} - {result.text}")

asyncio.run(main())
```

## Configuration

### Environment Variables

Set these environment variables to configure the client:

```bash
export COLBERT_HOST=localhost
export COLBERT_PORT=50051
export COLBERT_TIMEOUT=30.0
export COLBERT_MAX_RETRIES=3
export COLBERT_SECURE=false
```

### Programmatic Configuration

```python
from re_client import ColBERTClient, ClientConfig

# Using config object
config = ClientConfig(
    host="my-server.com",
    port=50051,
    timeout=60.0,
    secure=True
)

client = ColBERTClient(
    host=config.host,
    port=config.port,
    timeout=config.timeout,
    secure=config.secure
)

# Or directly
client = ColBERTClient(
    host="my-server.com",
    port=50051,
    timeout=60.0,
    secure=True
)
```

## Advanced Features

### Batch Processing

For large document sets, use batch processing:

```python
from re_client import ColBERTClient, batch_rerank

client = ColBERTClient()

# Process 1000 documents in batches of 100
large_doc_list = ["document " + str(i) for i in range(1000)]

response = batch_rerank(
    client=client,
    query="search query",
    documents=large_doc_list,
    batch_size=100
)
```

### Filtering Results

```python
from re_client import filter_by_score_threshold, get_top_k_with_threshold

# Filter by minimum score
filtered = filter_by_score_threshold(response, threshold=0.5)

# Get top 5 results with minimum score
top_results = get_top_k_with_threshold(response, k=5, threshold=0.3)
```

### Score Statistics

```python
from re_client import calculate_score_statistics

stats = calculate_score_statistics(response)
print(f"Mean score: {stats['mean_score']:.4f}")
print(f"Max score: {stats['max_score']:.4f}")
print(f"Min score: {stats['min_score']:.4f}")
```

### Error Handling

```python
from re_client import (
    ColBERTClient,
    ColBERTConnectionError,
    ColBERTServerError,
    ColBERTTimeoutError,
    ColBERTValidationError
)

client = ColBERTClient()

try:
    response = client.rerank("query", ["doc1", "doc2"])
except ColBERTConnectionError:
    print("Cannot connect to server")
except ColBERTTimeoutError:
    print("Request timed out")
except ColBERTValidationError as e:
    print(f"Invalid input: {e}")
except ColBERTServerError as e:
    print(f"Server error: {e}")
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

### ColBERTClient

Main client class for interacting with the server.

#### Methods

- `rerank(query, documents, timeout=None)` - Synchronous reranking
- `rerank_async(query, documents, timeout=None)` - Asynchronous reranking
- `health_check(timeout=None)` - Check server health
- `health_check_async(timeout=None)` - Async health check

#### Parameters

- `host` (str): Server hostname (default: "localhost")
- `port` (int): Server port (default: 50051)
- `timeout` (float): Request timeout in seconds (default: 30.0)
- `max_retries` (int): Maximum retry attempts (default: 3)
- `secure` (bool): Use secure connection (default: False)
- `credentials` (grpc.ChannelCredentials): gRPC credentials for secure connections

### RerankResponse

Response object containing reranking results.

#### Properties

- `results` (List[RerankResult]): List of ranked results

#### Methods

- `top_k(k)` - Get top k results
- `get_by_original_index(index)` - Get result by original document index
- `__len__()` - Number of results
- `__iter__()` - Iterate over results

### RerankResult

Individual reranking result.

#### Properties

- `original_index` (int): Original document index
- `score` (float): Relevance score
- `text` (str): Document text

## Examples

See the `examples/` directory for more usage examples:

- `basic_example.py` - Basic synchronous usage
- `async_example.py` - Asynchronous usage
- `batch_example.py` - Batch processing
- `advanced_example.py` - Advanced features and error handling

## Requirements

- Python 3.8+
- grpcio >= 1.50.0
- protobuf >= 4.0.0

## License

MIT License
