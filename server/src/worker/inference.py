import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import onnxruntime as ort
from numpy import array, clip, int64, linalg, matmul, ndarray, transpose
from numpy import max as np_max
from numpy import sum as np_sum
from tokenizers import Tokenizer

from logger import get_logger

_session = None
_tokenizer = None


logger = get_logger()


def start_session(model_path: str) -> None:
    global _session
    sess_options = ort.SessionOptions()
    ort_single_threaded = os.environ.get("ORT_SINGLE_THREADED", "false") == "true"
    if ort_single_threaded:
        logger.info("Using single-threaded ONNXRuntime")
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

    _session = ort.InferenceSession(
        model_path,
        sess_options=ort.SessionOptions(),
        providers=["CPUExecutionProvider"],
    )


def start_tokenizer(tokenizer_path: str) -> None:
    global _tokenizer
    _tokenizer = Tokenizer.from_file(tokenizer_path)


class RerankerPool:
    """Thread-based inference pool that works better with asyncio"""

    def __init__(self, model_path: str, tokenizer_path: str, pool_size: int = 1):
        self.pool_size = pool_size
        self.executor = ThreadPoolExecutor(max_workers=pool_size)

        # Initialize models in the main thread
        start_session(model_path)
        start_tokenizer(tokenizer_path)

        logger.info(
            "Created Reranker pool with %d workers (model: %s, tokenizer: %s)",
            pool_size,
            model_path,
            tokenizer_path,
        )

    def apply(self, func, args):
        """Apply function with args in thread pool"""
        future = self.executor.submit(func, *args)
        return future.result()

    def close(self):
        """Close the thread pool"""
        self.executor.shutdown(wait=False)

    def join(self):
        """Wait for all threads to complete"""
        self.executor.shutdown(wait=True)


def create_pool(
    model_path: str,
    tokenizer_path: str,
    pool_size: int = 1,
) -> RerankerPool:
    """Create a thread-based inference pool."""
    return RerankerPool(model_path, tokenizer_path, pool_size)


def inference(text_list, max_length):
    global _session, _tokenizer

    assert _tokenizer is not None
    assert _session is not None

    _tokenizer.enable_truncation(max_length=max_length)
    _tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=max_length)

    encodings = _tokenizer.encode_batch(text_list)

    input_ids = array([e.ids for e in encodings], dtype=int64)
    attention_mask = array([e.attention_mask for e in encodings], dtype=int64)

    onnx_inputs = {"input_ids": input_ids, "attention_mask": attention_mask}

    token_type_ids = array([e.type_ids for e in encodings], dtype=int64)
    onnx_inputs["token_type_ids"] = token_type_ids

    outputs = _session.run(None, onnx_inputs)

    embeddings = outputs[0]

    norms = linalg.norm(embeddings, axis=2, keepdims=True)  # type: ignore
    embeddings = embeddings / clip(norms, a_min=1e-12, a_max=None)

    return embeddings, attention_mask


def compute_scores(
    Q_emb: ndarray,
    D_emb: ndarray,
    q_mask: ndarray,
) -> ndarray:
    """Compute scores for each document."""
    D_emb_T = transpose(D_emb, (0, 2, 1))
    scores_matrix = matmul(Q_emb, D_emb_T)
    max_scores = np_max(scores_matrix, axis=2)
    q_valid_tokens = q_mask[0] == 1
    final_scores = np_sum(max_scores[:, q_valid_tokens], axis=1)
    return final_scores


def inference_and_score(query, documents, max_len_q, max_len_d):
    Q_emb, q_mask = inference([query], max_len_q)
    D_emb, _ = inference(documents, max_len_d)
    scores = compute_scores(Q_emb, D_emb, q_mask)
    return scores


async def rerank(
    query: str,
    documents: list[str],
    max_len_q: int,
    max_len_d: int,
    inference_pool: RerankerPool,
) -> ndarray:
    """Run prediction using thread pool."""
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            inference_pool.executor,
            inference_and_score,
            query,
            documents,
            max_len_q,
            max_len_d,
        )
        return result
    except Exception as e:
        logger.error("Error predicting: %s", e)
        return array([])
