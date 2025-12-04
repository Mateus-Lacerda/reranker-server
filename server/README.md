# ReServer Reranker Server

A high-performance gRPC server for document reranking using ReServer model with ONNX Runtime inference. The server provides efficient document relevance scoring through a thread-based inference pool.

## Overview

The ReServer Reranker Server is designed for production use cases requiring fast and accurate document reranking. It uses ONNX Runtime for optimized inference and supports concurrent request processing through a configurable worker pool.

### Key Features

- **High Performance**: ONNX Runtime-based inference with CPU optimization
- **Concurrent Processing**: Thread pool executor for handling multiple requests
- **Scalable Architecture**: Configurable worker pool size
- **Production Ready**: Docker containerization with multi-stage builds
- **gRPC Interface**: Efficient binary protocol for client-server communication
- **Environment Configuration**: Flexible configuration through environment variables

## Architecture

```
┌─────────────────┐
│   gRPC Server   │
│   (Port 50051)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Reranker Pool   │
│ (Thread Pool)   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ ONNX Runtime    │
│ ReServer Model   │
└─────────────────┘
```

## Quick Start

### Using Docker (Recommended)

```bash
# Pull and run the server
docker run -p 50051:50051 ghcr.io/Mateus-Lacerda/reranker-server:latest

# Or with custom configuration
docker run -p 50051:50051 \
  -e POOL_SIZE=4 \
  -e SERVER_PORT=50051 \
  ghcr.io/Mateus-Lacerda/reranker-server:latest
```

### Development Setup

```bash
# Install dependencies
cd server
uv sync

# Prepare model (if not using Docker)
cd model
chmod +x export_model.sh
./export_model.sh --full

# Run the server
cd ..
uv run python -m src.server

# Or run directly
uv run python __main__.py
```

### Testing the Server

```bash
# Run test client
uv run python src/test_server.py

# Or use the SDK
cd ../sdk
uv run python examples/basic_example.py
```

## Configuration

The server is configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `POOL_SIZE` | `1` | Number of inference worker threads |
| `MODEL_PATH` | `model/onnx_full/model.onnx` | Path to ONNX model file |
| `TOKENIZER_PATH` | `model/onnx_full/tokenizer.json` | Path to tokenizer file |
| `SERVER_PORT` | `50051` | gRPC server port |

### Example Configuration

```bash
# Production configuration
export POOL_SIZE=8
export MODEL_PATH=/app/models/colbert_v2.onnx
export TOKENIZER_PATH=/app/models/tokenizer.json
export SERVER_PORT=50051

# Start server
uv run python -m src.server
```

## API Reference

### gRPC Service Definition

```protobuf
syntax = "proto3";

package reranker;

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

### Service Implementation

The server implements the `RerankService` with the following behavior:

#### Rerank Method

**Input:**
- `query`: Search query string
- `documents`: List of documents to rerank

**Output:**
- `results`: List of `RerankResult` objects sorted by relevance score (descending)

**Processing:**
1. Validates input parameters
2. Tokenizes query and documents
3. Runs ReServer inference through ONNX Runtime
4. Calculates relevance scores
5. Sorts results by score
6. Returns ranked results

#### Constraints

- **Query Length**: Maximum 32 tokens (configurable via `MAX_LEN_Q`)
- **Document Length**: Maximum 180 tokens (configurable via `MAX_LEN_D`)
- **Empty Inputs**: Returns empty response for empty document lists

## Model Architecture

### ReServer Model

The server uses a ReServer (Contextualized Late Interaction over BERT) model exported to ONNX format:

- **Input**: Tokenized text sequences
- **Output**: Contextualized embeddings
- **Scoring**: Late interaction through maximum similarity

### ONNX Runtime Configuration

- **Providers**: CPU Execution Provider (optimized for CPU inference)
- **Session Options**: Default ONNX Runtime session configuration
- **Memory Management**: Automatic memory management with garbage collection

### Model Export

The model export process is handled by the `model/export_model.sh` script:

```bash
cd model

# Export full precision model (better accuracy)
./export_model.sh --full

# Export optimized model (faster inference)
./export_model.sh --optimized
```

## Performance

### Benchmarks

Performance characteristics (approximate, hardware-dependent):

| Metric | Single Worker | 4 Workers | 8 Workers |
|--------|---------------|-----------|-----------|
| **Throughput** | ~50 req/s | ~180 req/s | ~320 req/s |
| **Latency (P50)** | ~20ms | ~25ms | ~30ms |
| **Latency (P95)** | ~40ms | ~50ms | ~60ms |
| **Memory Usage** | ~1.2GB | ~1.5GB | ~2.0GB |

### Optimization Guidelines

1. **Worker Pool Size**: Set `POOL_SIZE` to match CPU cores (typically 2-8)
2. **Memory**: Ensure sufficient RAM (2-4GB recommended)
3. **CPU**: Multi-core systems provide better throughput
4. **Batch Size**: Client-side batching improves efficiency

## Deployment

### Docker

```bash
# Build image
docker build -t re-server .

# Run container
docker run -d \
  --name re-server \
  -p 50051:50051 \
  -e POOL_SIZE=4 \
  re-server
```


## Development

### Project Structure

```
server/
├── src/
│   ├── server.py           # Main gRPC server
│   ├── test_server.py      # Test client
│   ├── worker/
│   │   └── inference.py    # ONNX inference engine
│   ├── reranker_pb2.py     # Generated protobuf code
│   └── reranker_pb2_grpc.py # Generated gRPC code
├── model/
│   ├── export_model.sh     # Model export script
│   ├── onnx_full/          # Full precision model
│   └── README.md           # Model documentation
├── Dockerfile              # Container definition
├── pyproject.toml          # Dependencies
└── __main__.py             # Entry point
```

### Building from Source

```bash
# Install dependencies
cd server
uv sync

# Generate protobuf files (if needed)
cd ..
bash scripts/compile_protos.sh

# Export model
cd server/model
./export_model.sh --full

# Run server
cd ..
uv run python -m src.server
```

### Running Tests

```bash
# Unit tests
cd server
uv run pytest

# Integration test
uv run python src/test_server.py

# Load test (requires server running)
cd ../sdk
uv run python examples/load_test.py
```

### Code Quality

```bash
# Format code
cd server
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/
```

## Monitoring and Logging

### Logging Configuration

The server uses Python's standard logging module:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Server logs include:
# - Request processing times
# - Error conditions
# - Pool status
# - Model loading events
```

### Health Checks

For production deployments, implement health checks:

```bash
# Using grpc_health_probe
grpc_health_probe -addr=localhost:50051

# Using custom health check
curl -X POST http://localhost:8080/health
```

### Metrics

Key metrics to monitor:

- **Request Rate**: Requests per second
- **Response Time**: P50, P95, P99 latencies
- **Error Rate**: Failed requests percentage
- **Memory Usage**: RAM consumption
- **CPU Usage**: CPU utilization
- **Queue Depth**: Pending requests in thread pool

## Requirements

### System Requirements

- **Python**: 3.12+
- **Memory**: 2-4GB RAM (depending on model and pool size)
- **CPU**: Multi-core recommended (4+ cores for production)
- **Storage**: 2GB for model files
- **Network**: Port 50051 accessible

### Dependencies

Core dependencies (see `pyproject.toml`):

- `grpcio >= 1.76.0`: gRPC framework
- `grpcio-tools >= 1.76.0`: Protocol buffer compiler
- `numpy >= 2.3.5`: Numerical computing
- `onnxruntime >= 1.23.2`: ONNX model inference
- `tokenizers >= 0.21.4`: Text tokenization

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Mateus-Lacerda/reranker-server/issues)
- **Documentation**: [Server Documentation](README.md)
