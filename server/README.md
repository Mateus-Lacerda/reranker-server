# Reranker Server

A high-performance gRPC server for document reranking using ColBERT v2.0 model with ONNX runtime.

## Features

- **Fast inference**: ONNX-optimized ColBERT v2.0 model
- **gRPC API**: High-performance protocol buffers communication
- **Thread pool**: Configurable worker pool for concurrent requests
- **Easy deployment**: Simple setup with UV package manager

## Quick Start

### 1. Install Dependencies

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Download Model

Choose between full precision (FP32) or optimized (quantized) model:

```bash
# Full precision model (better accuracy, larger size)
cd model
chmod +x export_model.sh
./export_model.sh --full

# OR optimized model (faster inference, smaller size)
./export_model.sh --optimized
```

### 3. Start Server

```bash
# Start with default settings (port 50051, 1 worker)
uv run python server/server.py

# Or with custom configuration
POOL_SIZE=4 SERVER_PORT=50052 uv run python server/server.py
```

### 4. Test Server

```bash
# Run the test client
uv run python server/test_server.py
```

## Configuration

Environment variables:

- `MODEL_PATH`: Path to ONNX model file (default: `model/onnx_full/model.onnx`)
- `TOKENIZER_PATH`: Path to tokenizer file (default: `model/onnx_full/tokenizer.json`)
- `POOL_SIZE`: Number of worker threads (default: `1`)
- `SERVER_PORT`: Server port (default: `50051`)

## API Usage

The server exposes a `Rerank` RPC method that takes a query and list of documents, returning ranked results with scores.

### Request Format
```protobuf
message RerankRequest {
  string query = 1;
  repeated string documents = 2;
}
```

### Response Format
```protobuf
message RerankResponse {
  repeated RerankResult results = 1;
}

message RerankResult {
  int32 original_index = 1;
  float score = 2;
  string text = 3;
}
```

## Development

### Generate gRPC Files

```bash
cd server
chmod +x compile_protos.sh
./compile_protos.sh
```

### Project Structure

```
reranker-server/
├── server/           # gRPC server implementation
│   ├── server.py     # Main server
│   ├── test_server.py # Test client
│   └── reranker.proto # Protocol definition
├── worker/           # Inference engine
│   └── inference.py  # ONNX inference logic
├── model/            # Model export utilities
│   └── export_model.sh # Model download script
└── pyproject.toml    # Dependencies
```

## Requirements

- Python 3.12+
- UV package manager
- 4GB+ RAM (for full model)
- CPU with AVX2 support recommended
