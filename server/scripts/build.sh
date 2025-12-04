set -e
./scripts/compile_protos.sh

docker build -t re-server \
  --build-arg POOL_SIZE=1 \
  --build-arg MODEL_PATH="model/onnx_full/model.onnx" \
  --build-arg TOKENIZER_PATH="model/onnx_full/tokenizer.json" \
  --build-arg SERVER_PORT=50051 \
  .
set +e
