from __future__ import print_function

import os

from grpc import ServicerContext, StatusCode, aio
from grpc_health.v1.health import HealthServicer
from grpc_health.v1.health_pb2 import HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import add_HealthServicer_to_server

from logger import get_logger, log_time
from reranker_pb2 import RerankRequest, RerankResponse, RerankResult
from reranker_pb2_grpc import RerankServiceServicer, add_RerankServiceServicer_to_server
from worker.inference import RerankerPool, create_pool, rerank

logger = get_logger()


class OnnxRerankerService(RerankServiceServicer):
    def __init__(self, pool: RerankerPool):
        super().__init__()

        self.pool = pool
        self.MAX_LEN_Q = 32
        self.MAX_LEN_D = 180
        logger.info("Service is ready!")

    @log_time(logger)
    async def Rerank(
        self, request: RerankRequest, context: ServicerContext
    ) -> RerankResponse:
        logger.info("Reranking %s documents", len(request.documents))
        query = request.query
        documents = list(request.documents)

        if not documents:
            return RerankResponse(results=[])

        try:
            final_scores = await rerank(
                query, documents, self.MAX_LEN_Q, self.MAX_LEN_D, self.pool
            )
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
            logger.error("Error: %s", e)
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
    logger.info("Starting server on port %s", server_port)
    logger.info("Model path: %s", model_path)
    logger.info("Tokenizer path: %s", tokenizer_path)
    logger.info("Pool size: %s", pool_size)
    add_RerankServiceServicer_to_server(OnnxRerankerService(pool), server)
    health_servicer = HealthServicer()
    health_servicer.set("", HealthCheckResponse.ServingStatus.SERVING)
    add_HealthServicer_to_server(health_servicer, server)
    server.add_insecure_port(f"[::]:{server_port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
