# Documentation Index

This document provides an overview of all available documentation for the ReServer Reranker Server project.

## Project Overview

The ReServer Reranker Server is a high-performance document reranking service that consists of two main components:

1. **Server**: A gRPC-based reranking service using ReServer model with ONNX Runtime
2. **SDK**: A Python client library for easy integration with the reranking server

## Documentation Structure

### Main Documentation

- **[README.md](README.md)** - Project overview, quick start, and general information
  - Architecture overview
  - Features and capabilities
  - Quick start guide
  - Configuration reference
  - Deployment instructions
  - Performance benchmarks

### Component Documentation

#### Server Documentation

- **[server/README.md](server/README.md)** - Complete server documentation
  - Server architecture and features
  - Installation and setup
  - Configuration options
  - API reference (gRPC service)
  - Performance optimization
  - Docker and Kubernetes deployment
  - Monitoring and troubleshooting
  - Development guidelines

#### SDK Documentation

- **[sdk/README.md](sdk/README.md)** - Python SDK documentation
  - Installation instructions
  - Quick start examples
  - Configuration options
  - Complete API reference
  - Error handling
  - Utility functions
  - Development guidelines

#### Model Documentation

- **[server/model/README.md](server/model/README.md)** - Model-specific documentation
  - Model architecture and specifications
  - Export and setup instructions
  - Performance characteristics
  - Customization options
  - Troubleshooting

### Deployment Documentation

- **[.github/DEPLOYMENT.md](.github/DEPLOYMENT.md)** - CI/CD and deployment setup
  - GitHub Actions pipelines
  - PyPI and Docker Hub configuration
  - Release process
  - Environment setup

## Quick Navigation

### For Developers

If you're developing with the SDK:
1. Start with [sdk/README.md](sdk/README.md)
2. Check examples in `sdk/examples/`
3. Refer to the main [README.md](README.md) for server setup

### For DevOps/Infrastructure

If you're deploying the server:
1. Read [server/README.md](server/README.md) for deployment options
2. Check [.github/DEPLOYMENT.md](.github/DEPLOYMENT.md) for CI/CD setup
3. Review [server/model/README.md](server/model/README.md) for model requirements

### For Contributors

If you're contributing to the project:
1. Start with the main [README.md](README.md)
2. Read development sections in both [server/README.md](server/README.md) and [sdk/README.md](sdk/README.md)
3. Check [.github/DEPLOYMENT.md](.github/DEPLOYMENT.md) for release process

## Getting Started

### 1. Quick Start (Users)

```bash
# Run the server
docker run -p 50051:50051 ghcr.io/Mateus-Lacerda/reranker-server:latest

# Install and use the SDK
pip install reserver-client
python -c "
from re_client import ReServerClient
client = ReServerClient()
response = client.rerank('query', ['doc1', 'doc2'])
print(response.results)
"
```

### 2. Development Setup

```bash
# Clone repository
git clone <repository-url>
cd reranker-server

# Setup server
cd server && uv sync

# Setup SDK
cd ../sdk && uv sync

# Compile protocols
bash scripts/compile_protos.sh

# Run server
cd server && uv run python -m src.server

# Test SDK
cd ../sdk && uv run python examples/basic_example.py
```

### 3. Production Deployment

See [server/README.md](server/README.md) for detailed deployment instructions including:
- Docker deployment
- Kubernetes manifests
- Load balancing
- Monitoring setup

## API Overview

### gRPC Service

```protobuf
service RerankService {
  rpc Rerank (RerankRequest) returns (RerankResponse) {}
}
```

### Python SDK

```python
from re_client import ReServerClient

client = ReServerClient(host="localhost", port=50051)
response = client.rerank(query="search query", documents=["doc1", "doc2"])
```

## Configuration Reference

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POOL_SIZE` | `1` | Number of inference workers |
| `MODEL_PATH` | `model/onnx_full/model.onnx` | Path to ONNX model |
| `TOKENIZER_PATH` | `model/onnx_full/tokenizer.json` | Path to tokenizer |
| `SERVER_PORT` | `50051` | gRPC server port |

### SDK Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RESERVER_HOST` | `localhost` | Server hostname |
| `RESERVER_PORT` | `50051` | Server port |
| `RESERVER_TIMEOUT` | `30.0` | Request timeout (seconds) |
| `RESERVER_MAX_RETRIES` | `3` | Maximum retry attempts |

## Support and Resources

- **Issues**: [GitHub Issues](https://github.com/Mateus-Lacerda/reranker-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Mateus-Lacerda/reranker-server/discussions)

## Contributing

1. Read the main [README.md](README.md) for project overview
2. Check development sections in component documentation
3. Follow the contribution guidelines in each component
4. Submit pull requests with appropriate tests and documentation

## License

This project is licensed under the MIT License. See the LICENSE file for details.
