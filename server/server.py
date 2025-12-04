import os

import numpy as np
from grpc import ServicerContext, StatusCode, aio
from reranker_pb2 import RerankRequest, RerankResponse, RerankResult
from reranker_pb2_grpc import RerankServiceServicer, add_RerankServiceServicer_to_server

from worker.inference import RerankerPool, create_pool, rerank


class OnnxRerankerService(RerankServiceServicer):
    def __init__(self, pool: RerankerPool):
        super().__init__()

        self.pool = pool
        self.MAX_LEN_Q = 32
        self.MAX_LEN_D = 180
        print("Service is ready!")

    async def Rerank(
        self, request: RerankRequest, context: ServicerContext
    ) -> RerankResponse:
        query = request.query
        documents = list(request.documents)

        if not documents:
            return RerankResponse(results=[])

        try:
            Q_emb, q_mask = await rerank([query], self.MAX_LEN_Q, self.pool)
            D_emb, d_mask = await rerank(documents, self.MAX_LEN_D, self.pool)
            D_emb_T = np.transpose(D_emb, (0, 2, 1))
            scores_matrix = np.matmul(Q_emb, D_emb_T)
            max_scores = np.max(scores_matrix, axis=2)
            q_valid_tokens = q_mask[0] == 1
            final_scores = np.sum(max_scores[:, q_valid_tokens], axis=1)
            results = []
            for i, score in enumerate(final_scores):
                results.append(
                    RerankResult(
                        original_index=i,
                        score=float(score),
                        text=documents[i],
                    )
                )

            results.sort(key=lambda x: x.score, reverse=True)

            return RerankResponse(results=results)

        except Exception as e:
            print(f"Error: {e}")
            context.set_details(str(e))
            context.set_code(StatusCode.INTERNAL)
            return RerankResponse()


async def serve():
    pool_size = int(os.getenv("POOL_SIZE", "1"))
    model_path = os.getenv("MODEL_PATH", "model/onnx_full/model.onnx")
    tokenizer_path = os.getenv("TOKENIZER_PATH", "model/onnx_full/tokenizer.json")
    pool = create_pool(model_path, tokenizer_path, pool_size)

    server_port = int(os.getenv("SERVER_PORT", "50051"))
    server = aio.server()
    add_RerankServiceServicer_to_server(OnnxRerankerService(pool), server)
    server.add_insecure_port(f"[::]:{server_port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
