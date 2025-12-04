#!/bin/bash

set -e

MODEL_ID="colbert-ir/colbertv2.0"

if [ -z "$1" ]; then
    echo "Error: No arguments provided."
    echo "Usage: $0 [--full | --optimized]"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first."
    exit 1
fi

case "$1" in
    --full)
        echo "Exporting FULL model (FP32)..."
        echo "Destination: ./onnx_full"

        uv run python -m optimum.exporters.onnx \
            --model $MODEL_ID \
            --task feature-extraction \
            onnx_full/
            
        echo "Success! FP32 model saved to onnx_full/"
        ;;

    --optimized)
        echo "Exporting OPTIMIZED model (Dynamic Quantization Int8)..."
        echo "Destination: ./onnx_opt"
        
        uv run python -m optimum.exporters.onnx \
            --model $MODEL_ID \
            --task feature-extraction \
            --quantize dynamic \
            onnx_opt/
            
        echo "Success! Quantized model saved to onnx_opt/"
        ;;

    *)
        echo "Invalid option: $1"
        echo "Usage: $0 [--full | --optimized]"
        exit 1
        ;;
esac
