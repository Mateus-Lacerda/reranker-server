# ReServer Reranker Server

A high-performance document reranking service built with ReServer model, featuring a gRPC server and Python SDK for efficient document relevance scoring.

## Overview

This project provides a complete solution for document reranking using ReServer (Contextualized Late Interaction over BERT). It consists of two main components:

- **Server**: A gRPC-based reranking service that runs ReServer inference using ONNX Runtime
- **SDK**: A Python client library for easy integration with the reranking server

## Architecture

```
┌─────────────────┐    gRPC     ┌─────────────────┐
│   Client App    │ ◄─────────► │  Reranker       │
│   (uses SDK)    │             │  Server         │
└─────────────────┘             └─────────────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  ReServer Model │
                                │  (ONNX Runtime) │
                                └─────────────────┘
```

## Features

- **Optimized Performance**: ONNX Runtime-based inference with configurable thread pool (1-3 RPS typical)
- **Scalable**: Configurable worker pool for concurrent request handling in horizontably scalable environments
- **Easy Integration**: Python SDK with both sync and async support
- **Production Ready**: Docker containerization with multi-stage builds

## Quick Start

### Using Docker (Recommended)

```bash
# Pull and run the server
docker run -p 50051:50051 ghcr.io/Mateus-Lacerda/reranker-server:latest

# Install the SDK
pip install reserver-client

# Use in your Python code
from re_client import ReServerClient

client = ReServerClient()
response = client.rerank(
    query="machine learning frameworks",
    documents=[
        "TensorFlow is a machine learning library",
        "React is a web development framework",
        "PyTorch is used for deep learning"
    ]
)

for result in response.results:
    print(f"Score: {result.score:.4f} - {result.text}")
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Mateus-Lacerda/reranker-server.git
cd reranker-server

# Install dependencies (requires uv)
cd server && uv sync
cd ../sdk && uv sync

# Compile protocol buffers
bash scripts/compile_protos.sh

# Run the server
cd server && uv run python -m src.server

# Test with the SDK
cd sdk && uv run python examples/basic_example.py
```

## Components

### Server
The reranking server provides a gRPC service for document reranking using ReServer model.

**Key Features:**
- ONNX Runtime-based inference
- Thread pool for concurrent processing
- Configurable model and tokenizer paths
- Environment-based configuration

**Documentation**: [Server Documentation](server/README.md)

### SDK
Python client library for interacting with the reranking server.

**Key Features:**
- Synchronous and asynchronous clients
- Automatic retry and error handling
- Type-safe request/response models
- Utility functions for batch processing

**Documentation**: [SDK Documentation](sdk/README.md)

## Configuration

### Server Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `POOL_SIZE` | `1` | Number of inference workers |
| `MODEL_PATH` | `model/onnx_full/model.onnx` | Path to ONNX model file |
| `TOKENIZER_PATH` | `model/onnx_full/tokenizer.json` | Path to tokenizer file |
| `SERVER_PORT` | `50051` | gRPC server port |

### SDK Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RESERVER_HOST` | `localhost` | Server hostname |
| `RESERVER_PORT` | `50051` | Server port |
| `RESERVER_TIMEOUT` | `30.0` | Request timeout (seconds) |
| `RESERVER_MAX_RETRIES` | `3` | Maximum retry attempts |
| `RESERVER_SECURE` | `false` | Use secure connection |

## API Reference

### gRPC Service

```protobuf
service RerankService {
  rpc Rerank (RerankRequest) returns (RerankResponse) {}
}

message RerankRequest {
  string query = 1;
  repeated string documents = 2;
}

message RerankResponse {
  repeated RerankResult results = 1;
}

message RerankResult {
  int32 original_index = 1;
  float score = 2;
  string text = 3;
}
```

### Python SDK

```python
from re_client import ReServerClient

# Create client
client = ReServerClient(host="localhost", port=50051)

# Synchronous reranking
response = client.rerank(query="search query", documents=["doc1", "doc2"])

# Asynchronous reranking
response = await client.rerank_async(query="search query", documents=["doc1", "doc2"])

# Health check
is_healthy = client.health_check()
```

## Deployment

### Docker

```bash
# Build the image
docker build -t reranker-server ./server

# Run with custom configuration
docker run -p 50051:50051 \
  -e POOL_SIZE=4 \
  -e MODEL_PATH=/app/model/custom_model.onnx \
  reranker-server
```


## Performance

### Benchmarks

Based on stress testing with Intel i7-13620H (16 cores), 64GB RAM, POOL_SIZE=2:

#### **Throughput (Requests per Second)**
- **Light Load**: 1-2 RPS sustained
- **Production Load**: 0.5-1.5 RPS typical
- **Stress Test**: 0.7 RPS average under extreme load (500 concurrent users)
- **Peak Performance**: Up to 3 RPS with optimized configuration

#### **Latency by Document Count**
- **Single Document**: ~180ms average, ~220ms p95
- **Standard Reranking (3-10 docs)**: ~690ms average, ~1000ms p95
- **Large Sets (15-25 docs)**: ~1700ms average, ~2100ms p95
- **Maximum Load (50+ docs)**: ~3300ms average, ~3900ms p95
- **Empty Requests**: ~2ms average, ~10ms p95

#### **Resource Requirements**
- **Memory**: 2-4GB RAM (including model and inference pool)
- **CPU**: Expect 80-100% utilization under load (ML inference is CPU-intensive)
- **Storage**: ~500MB for ONNX model files
- **Network**: Low bandwidth requirements (~1-10KB per request)

#### **Scaling Characteristics**
- **Document Count Impact**: Latency scales roughly linearly with document count
- **Concurrent Users**: Performance degrades gracefully under high concurrency
- **Worker Pool**: Increase POOL_SIZE to match CPU cores for optimal throughput
- **Horizontal Scaling**: Deploy multiple instances for higher aggregate throughput

### Optimization Tips

#### **Server Configuration**
1. **Increase Pool Size**: Set `POOL_SIZE` to match your CPU cores
   - `POOL_SIZE=2`: ~0.7-1.5 RPS (tested)
   - `POOL_SIZE=4`: ~1.5-3.0 RPS (estimated)
   - `POOL_SIZE=8+`: ~3.0-6.0 RPS (estimated, diminishing returns)

2. **Hardware Optimization**:
   - Use high single-core performance CPUs for ML inference
   - Allocate 4-8GB RAM for stable operation under load
   - SSD storage recommended for model loading

#### **Application Optimization**
3. **Batch Requests**: Use SDK utilities for batch processing
4. **Connection Pooling**: Reuse client instances to reduce overhead
5. **Request Optimization**: Limit document count per request (optimal: 3-10 documents)
6. **Caching**: Implement result caching for repeated queries

#### **Production Deployment**
7. **Load Balancing**: Deploy multiple server instances behind a load balancer
8. **Resource Limits**: Set appropriate Docker/K8s resource limits
9. **Monitoring**: Track CPU usage, memory consumption, and response times
10. **Auto-scaling**: Scale horizontally based on CPU utilization (>80%)

## Development

### Prerequisites

- Python 3.8+ (SDK) / 3.12+ (Server)
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (for containerization)

### Building from Source

```bash
# Install dependencies
cd server && uv sync
cd ../sdk && uv sync

# Compile protocol buffers
bash scripts/compile_protos.sh

# Run tests
cd server && uv run pytest
cd ../sdk && uv run pytest

# Build packages
cd sdk && uv build
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Mateus-Lacerda/reranker-server/issues)
