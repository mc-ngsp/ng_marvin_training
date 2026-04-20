import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from strands import Agent, tool
from strands.models import BedrockModel

load_dotenv()

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

model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-east-1",
)

def generate_hypothetical_answer(query: str) -> str:
    """Generate a hypothetical answer to the query using the LLM.
    This is used for HyDE (Hypothetical Document Embeddings) to improve retrieval.

    Args:
        query: The user's query.
    """
    hyde_agent = Agent(
        model=model,
        system_prompt="You are a MontyCloud assistant and can answer any questions related to MontyCloud and CloudOps. Generate a detailed, factual-sounding passage that would answer the following question. Write as if it's an excerpt from a blog article.",
        callback_handler=None
    )
    response = hyde_agent(query)
    return str(response)


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
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(hyde_query)
    # nodes = retriever.retrieve(query)
    # nodes.extend(hyde_nodes)
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


agent = Agent(
    model=model,
    tools=[query_vector_db],
    system_prompt=(
        "You are a helpful MontyCloud assistant with access to a knowledge base of blog articles. "
        "Always use the query_vector_db tool to retrieve relevant information before answering."
        "Note: Always use the information retrieved from the vector database, don't add any additional information that is not supported by the retrieved results." 
        "Note: If the query_vector_db tool does not return any related information, say that the query is above your pay grade instead of trying to make up an answer. " 
        "Note: Don't say you are experiencing technical difficulties. Just say the query is above your pay grade."
    ),
)

if __name__ == "__main__":
    print("Monty Agent ready.\n")
    user_input = input("You: ").strip()
    agent(user_input)
