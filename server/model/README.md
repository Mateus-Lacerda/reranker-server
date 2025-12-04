# ReServer Model

This directory contains the ReServer model files and export utilities for the reranker server.

## Overview

The ReServer (Contextualized Late Interaction over BERT) model is exported to ONNX format for optimized inference. The model provides document reranking capabilities through contextualized embeddings and late interaction scoring.

## Model Files

After running the export script, the following files will be available:

```
model/
├── onnx_full/              # Full precision model
│   ├── model.onnx          # ONNX model file
│   ├── tokenizer.json      # Tokenizer configuration
│   ├── config.json         # Model configuration
│   ├── vocab.txt           # Vocabulary file
│   ├── tokenizer_config.json
│   └── special_tokens_map.json
├── export_model.sh         # Model export script
└── README.md               # This file
```

## Model Export

Use the export script to download and prepare the model:

```bash
cd model

# Export full precision model (recommended for accuracy)
chmod +x export_model.sh
./export_model.sh --full

# Export optimized model (faster inference, slightly lower accuracy)
./export_model.sh --optimized
```

### Export Options

- `--full`: Exports full precision (FP32) model
- `--optimized`: Exports quantized/optimized model for faster inference

## Model Specifications

### Architecture

- **Base Model**: BERT-based encoder
- **Model Type**: ReServer v2.0
- **Input Length**:
  - Query: Maximum 32 tokens
  - Document: Maximum 180 tokens
- **Output**: Contextualized embeddings for late interaction

### Performance Characteristics

| Model Type | Size | Accuracy | Inference Speed |
|------------|------|----------|----------------|
| Full (FP32) | ~400MB | High | Moderate |
| Optimized | ~100MB | Good | Fast |

### Input Format

The model expects tokenized input in the following format:

```
Input IDs: [CLS] query_tokens [SEP] document_tokens [SEP] [PAD]...
Attention Mask: [1, 1, ..., 1, 0, 0, ...]
Token Type IDs: [0, 0, ..., 0, 1, 1, ..., 1, 0, 0, ...]
```

### Output Format

The model outputs contextualized embeddings that are used for late interaction scoring:

- **Shape**: `(batch_size, sequence_length, hidden_size)`
- **Type**: Float32 tensors
- **Normalization**: L2 normalized embeddings

## Usage

The model is automatically loaded by the server when started. Configuration is handled through environment variables:

```bash
export MODEL_PATH=model/onnx_full/model.onnx
export TOKENIZER_PATH=model/onnx_full/tokenizer.json
```

## Customization

### Using Custom Models

To use a custom ReServer model:

1. Export your model to ONNX format
2. Place the files in a directory structure similar to `onnx_full/`
3. Update the environment variables to point to your model files

### Model Requirements

Custom models must:

- Be compatible with ONNX Runtime
- Accept the same input format (input_ids, attention_mask, token_type_ids)
- Output embeddings suitable for late interaction scoring
- Use the same tokenizer format

## Troubleshooting

### Model Loading Issues

```bash
# Verify model files exist
ls -la onnx_full/

# Check file permissions
chmod 644 onnx_full/*

# Re-export model
./export_model.sh --full
```

### Memory Issues

If you encounter memory issues:

1. Use the optimized model: `./export_model.sh --optimized`
2. Reduce the pool size in server configuration
3. Ensure sufficient system RAM (2GB+ recommended)

### Performance Issues

For better performance:

1. Use the full precision model for accuracy
2. Ensure CPU supports AVX2 instructions
3. Increase the server pool size to match CPU cores

## Model Updates

To update the model:

1. Remove existing model files: `rm -rf onnx_full/`
2. Run the export script again: `./export_model.sh --full`
3. Restart the server to load the new model

## License

The model files are subject to their respective licenses. Please check the original model repository for licensing information.
