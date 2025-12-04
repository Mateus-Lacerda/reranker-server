#!/bin/bash

set -e

MODEL_ID="colbert-ir/colbertv2.0"
FORCE=false

for arg in "$@"; do
    if [ "$arg" == "--force" ]; then
        FORCE=true
        break
    fi
done

if [ -z "$1" ]; then
    echo "Error: No arguments provided."
    echo "Usage: $0 [--full | --optimized] [--force]"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first."
    exit 1
fi

case "$1" in
    --full)
        TARGET_DIR="onnx_full"
        TARGET_FILE="$TARGET_DIR/model.onnx"
        
        if [ -f "$TARGET_FILE" ] && [ "$FORCE" = false ]; then
            echo "Model already exists at $TARGET_FILE."
            echo "Skipping export. Use --force to overwrite."
        else
            echo "Exporting FULL model (FP32)..."
            echo "Destination: ./$TARGET_DIR"

            uv run python -m optimum.exporters.onnx \
                --model $MODEL_ID \
                --task feature-extraction \
                "$TARGET_DIR/"
            
            echo "Success! FP32 model saved to $TARGET_DIR/"
        fi
        ;;

    --optimized)
        TARGET_DIR="onnx_opt"
        if { [ -f "$TARGET_DIR/model.onnx" ] || [ -f "$TARGET_DIR/model_quantized.onnx" ]; } && [ "$FORCE" = false ]; then
            echo " Optimized model already exists in $TARGET_DIR."
            echo "Skipping export. Use --force to overwrite."
        else
            echo "Exporting OPTIMIZED model (Dynamic Quantization Int8)..."
            echo "Destination: ./$TARGET_DIR"
            
            uv run python -m optimum.exporters.onnx \
                --model $MODEL_ID \
                --task feature-extraction \
                --quantize dynamic \
                "$TARGET_DIR/"
            
            echo "Success! Quantized model saved to $TARGET_DIR/"
        fi
        ;;

    *)
        if [ "$1" != "--force" ]; then
            echo "Invalid option: $1"
            echo "Usage: $0 [--full | --optimized] [--force]"
            exit 1
        fi
        ;;
esac
