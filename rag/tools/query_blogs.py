from llama_index.core import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from strands import tool
import chromadb

from agents.hyde_agent import build_hyde_agent

@tool
def query_vector_db(query: str) -> str:
    """Search the vector database for information relevant to the user's query.
    Use this to retrieve context from the blog articles before answering.

    Args:
        query: The search query to look up in the vector database.
    """
    print(f"Querying for {query}...")
    top_k = 5
    hyde_query = generate_hypothetical_answer(query)
    print(f"HyDE query generated. Querying vector database...")
    print(f"HyDE Query: {hyde_query[0:100]}")


    # Load Vector Store Index
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = chroma_client.get_or_create_collection("blogs")

    embedding_model = BedrockEmbedding(
        model_name="amazon.titan-embed-text-v2:0",
        region_name="us-east-1",
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context, embed_model=embedding_model
    )

    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(hyde_query)
    if not nodes:
        return "No relevant information found."
    results = []
    print(f"Found {len(nodes)} relevant nodes. Compiling results...")
    for i, node in enumerate(nodes, 1):
        print("Node Similarity Score:", node.score)
        if node.score < 0.5:
            continue
        results.append(f"[Result {i}]\n{node.get_content()}")
    return "\n\n".join(results)

def generate_hypothetical_answer(query: str) -> str:
    hyde_agent = build_hyde_agent()
    response = hyde_agent(query)
    return str(response)