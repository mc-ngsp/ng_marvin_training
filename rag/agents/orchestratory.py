
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands import Agent

from config import SESSION_DIR, MODEL_ID
from tools.query_blogs import query_vector_db

def build_orchestrator(session_id: str) -> Agent:
    session_manager = FileSessionManager(
        session_id=f"{session_id}_reviewer",
        storage_dir=SESSION_DIR,
    )

    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.3,
        preserve_recent_messages=10,
    )

    model = BedrockModel(
        model_id=MODEL_ID,
        region_name="us-east-1",
    )

    agent = Agent(
        model=model,
        tools=[query_vector_db],
        session_manager=session_manager,
        conversation_manager=conversation_manager,
        system_prompt=(
            "You are a helpful MontyCloud assistant with access to a knowledge base of blog articles. "
            "Always use the query_vector_db tool to retrieve relevant information before answering."
            "Note: Always use the information retrieved from the vector database, don't add any additional information that is not supported by the retrieved results." 
            "Note: If the query_vector_db tool does not return any related information, say that the query is above your pay grade instead of trying to make up an answer. " 
            "Note: Don't say you are experiencing technical difficulties. Just say the query is above your pay grade."
        ),
    )

    return agent