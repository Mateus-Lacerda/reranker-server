#!/bin/bash

set -e

PROTO_FILE="reranker.proto"

# Check if the proto file exists
if [ ! -f "$PROTO_FILE" ]; then
    echo "Error: File '$PROTO_FILE' not found."
    exit 1
fi

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "uv detected. Generating gRPC files via uv..."
    
    # Run using the environment managed by uv
    # Note: Ensure 'grpcio-tools' is added (uv add grpcio-tools)
    uv run python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. "$PROTO_FILE"

else
    echo "uv not found. Attempting to run with system python..."
    
    # Try running with standard python (requires grpcio-tools installed via pip)
    python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. "$PROTO_FILE"
fi

echo "Python files generated successfully for $PROTO_FILE!"
