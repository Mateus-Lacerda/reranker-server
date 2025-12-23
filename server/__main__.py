import asyncio
import os

from src.server import serve

run_single_threaded = os.environ.get("RUN_SINGLE_THREADED", "false").lower() == "true"

if run_single_threaded:
    from threadpoolctl import threadpool_limits, threadpool_info
    threadpool_limits(1)
    print("Running single-threaded.", flush=True)
    print(f"Threadpool info: {threadpool_info()}", flush=True)
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["ORT_SINGLE_THREADED"] = "true"

asyncio.run(serve())
