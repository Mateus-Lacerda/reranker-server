import grpc

from reranker_pb2 import RerankRequest
from reranker_pb2_grpc import RerankServiceStub


def run():
    # Server address (adjust port according to your server)
    server_address = "localhost:50051"

    print(f"📡 Connecting to server at {server_address}...")

    # Create insecure channel for local testing
    with grpc.insecure_channel(server_address) as channel:
        stub = RerankServiceStub(channel)

        # --- Test Data ---
        query_text = "how to install python dependencies fast"

        docs_list = [
            "The sky is blue and the day is beautiful.",  # Irrelevant
            "UV is an extremely fast Python package manager written in Rust.",  # Highly Relevant
            "Carrot cake recipe with chocolate.",  # Irrelevant
            "Pip is the standard installer for Python packages.",  # Relevant
            "The history of the Roman Empire.",  # Irrelevant
        ]

        print(f"\n🔍 Query: '{query_text}'")
        print(f"📄 Sending {len(docs_list)} documents for reranking...\n")

        # Create the request
        request = RerankRequest(query=query_text, documents=docs_list)

        try:
            # Make the RPC call
            response = stub.Rerank(request)

            print("✅ Response received:\n")
            print(f"{'RANK':<5} | {'SCORE':<10} | {'ORIGINAL INDEX':<15} | {'TEXT'}")
            print("-" * 80)

            # Iterate over results
            for i, result in enumerate(response.results):
                # Format score to 4 decimal places
                print(
                    f"{i + 1:<5} | {result.score:.4f}     | {result.original_index:<15} | {result.text}"
                )

        except grpc.RpcError as e:
            print(f"❌ gRPC call error: {e.code()}")
            print(f"Details: {e.details()}")


if __name__ == "__main__":
    run()
