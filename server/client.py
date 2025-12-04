import grpc

from reranker_pb2 import RerankRequest

# IMPORTANTE: Substitua 'service_pb2' e 'service_pb2_grpc' pelos nomes
# dos arquivos que foram gerados pelo comando no passo 2.
from reranker_pb2_grpc import RerankServiceStub


def run():
    # Endereço do servidor (ajuste a porta conforme seu servidor)
    server_address = "localhost:50051"

    print(f"📡 Tentando conectar ao servidor em {server_address}...")

    # Cria o canal de comunicação inseguro (para testes locais)
    with grpc.insecure_channel(server_address) as channel:
        stub = RerankServiceStub(channel)

        # --- Dados de Teste ---
        query_text = "como instalar dependencias python rapido"

        docs_list = [
            "O céu é azul e o dia está bonito.",  # Irrelevante
            "O uv é um gerenciador de pacotes Python extremamente rápido escrito em Rust.",  # Altamente Relevante
            "Receita de bolo de cenoura com chocolate.",  # Irrelevante
            "Pip é o instalador padrão para pacotes Python.",  # Relevante
            "A história do império romano.",  # Irrelevante
        ]

        print(f"\n🔍 Query: '{query_text}'")
        print(f"📄 Enviando {len(docs_list)} documentos para reranking...\n")

        # Cria a requisição
        request = RerankRequest(query=query_text, documents=docs_list)

        try:
            # Faz a chamada RPC
            response = stub.Rerank(request)

            print("✅ Resposta recebida:\n")
            print(f"{'RANK':<5} | {'SCORE':<10} | {'INDEX ORIGINAL':<15} | {'TEXTO'}")
            print("-" * 80)

            # Itera sobre os resultados
            for i, result in enumerate(response.results):
                # Formata o score para 4 casas decimais
                print(
                    f"{i + 1:<5} | {result.score:.4f}     | {result.original_index:<15} | {result.text}"
                )

        except grpc.RpcError as e:
            print(f"❌ Erro na chamada gRPC: {e.code()}")
            print(f"Detalhes: {e.details()}")


if __name__ == "__main__":
    run()
