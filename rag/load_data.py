from typing import List

import requests
import os
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import BaseNode
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb

load_dotenv()

website_links = [
    'https://montycloud.com/how-msps-can-scale-aws-security-assessments-and-win/',
    'https://montycloud.com/the-mcp-server-control-plane-great-power-great-responsibility/',
    'https://montycloud.com/leading-the-wave-introducing-montycloud-ai-and-the-autonomous-cloudops-revolution/',
    'https://montycloud.com/accelerating-autonomous-cloudops-with-montyclouds-new-cloudops-mcp-model-context-protocol-server/'
    ]

chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("blogs")

def load_data():
    embedding_model = BedrockEmbedding(
        model_name="amazon.titan-embed-text-v2:0",
        region_name="us-east-1",
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context, embed_model=embedding_model)

    for link in website_links:
        markdown = convert_to_markdown(link)
        nodes = chunk_markdown(markdown)
        print(f"Number of nodes for {link}: {len(nodes)}")
        for node in nodes:
            index.insert(node)

    print(f"Total number of nodes in collection: {chroma_collection.count()}")

def convert_to_markdown(url: str) -> str:
    response = requests.get(
        f"https://r.jina.ai/{url}",
        headers={
            # "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
            "X-Retain-Images": "none",
            "X-Return-Format": "markdown",
        },
    )
    response.raise_for_status()
    return response.text

def chunk_markdown(markdown: str) -> list[str]:
    parser = MarkdownNodeParser()
    doc = Document(text=markdown)
    nodes = parser.get_nodes_from_documents(documents=[doc], include_metadata=True, include_prev_next_rel=False)
    return nodes

def convert_to_embeddings(nodes: List[BaseNode]) -> list[tuple[str, list[float]]]:
    embeddings = BedrockEmbedding(
        model_name="amazon.titan-embed-text-v2:0",
        region_name="us-east-1",
    )
    node_embeddings = []
    for node in nodes:
        embedding = embeddings.get_text_embedding(node.get_content())
        node_embeddings.append((node.get_content(), embedding))
    return node_embeddings

if __name__ == "__main__":
    load_data()