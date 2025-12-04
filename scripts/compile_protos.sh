#!/bin/bash

set -e

PROTO_FILE="reranker.proto"

if [ ! -f "$PROTO_FILE" ]; then
    echo "Error: File '$PROTO_FILE' not found in root directory."
    exit 1
fi

generate_module() {
    MODULE_DIR=$1
    OUTPUT_DIR=$2

    echo "---------------------------------------------------"
    echo "Processing module: $MODULE_DIR"
    
    pushd "$MODULE_DIR" > /dev/null

    if command -v uv &> /dev/null; then
        echo "Using uv from $MODULE_DIR..."
        
        uv run python -c 'import grpc, google.protobuf; print(f"Using grpc: {grpc.__version__}, protobuf: {google.protobuf.__version__}")'

        echo "Generating gRPC files..."
        
        uv run python -m grpc_tools.protoc \
            -I.. \
            --python_out="$OUTPUT_DIR" \
            --pyi_out="$OUTPUT_DIR" \
            --grpc_python_out="$OUTPUT_DIR" \
            "../$PROTO_FILE"
            
    else
        echo "uv not found inside $MODULE_DIR. Skipping or failing..."
        exit 1
    fi

    popd > /dev/null
}

generate_module "server" "src"

generate_module "sdk" "re_client"

echo "---------------------------------------------------"
echo "Python files generated successfully for both projects!"
