#!/bin/bash

set -e

PROTO_FILE="reranker.proto"

if [ ! -f "$PROTO_FILE" ]; then
    echo "Error: File '$PROTO_FILE' not found."
    exit 1
fi

if command -v uv &> /dev/null; then
    echo "uv detected. Generating gRPC files via uv..."
    
    uv run python -m grpc_tools.protoc -I. --python_out=./server/src --pyi_out=./server/src --grpc_python_out=./server/src "$PROTO_FILE"
    uv run python -m grpc_tools.protoc -I. --python_out=./sdk/re_client --pyi_out=./sdk/re_client --grpc_python_out=./sdk/re_client "$PROTO_FILE"

else
    echo "uv not found. Attempting to run with system python..."
    
    # Try running with standard python (requires grpcio-tools installed via pip)
    python3 -m grpc_tools.protoc -I. --python_out./server/src --pyi_out./server/src --grpc_python_out./server/src "$PROTO_FILE"
    python3 -m grpc_tools.protoc -I. --python_out./sdk/re_client --pyi_out./sdk/re_client --grpc_python_out./sdk/re_client "$PROTO_FILE"
fi

echo "Python files generated successfully for $PROTO_FILE!"
