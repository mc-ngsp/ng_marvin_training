from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SummarizingConversationManager
from config import SESSION_DIR, MODEL_ID, REGION_NAME
from strands_tools import file_read, file_write

def build_file_operator_agent(session_id: str) -> Agent:
    session_manager = FileSessionManager(
        session_id=f"{session_id}_file_operator",
        storage_dir=SESSION_DIR,
    )

    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.3,
        preserve_recent_messages=10,
    )

    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION_NAME,
    )

    agent = Agent(
        name="File Operator Agent",
        model=model,
        tools=[file_read, file_write],
        session_manager=session_manager,
        conversation_manager=conversation_manager,
        system_prompt=(
            "You are a helpful assistant that can read from and write to files using the file_read and file_write tools."
            "Use the file_read tool to read the contents of a file when the user asks to see what's inside a file."
            "Use the file_write tool to write content to a file when the user asks you to save some information."
            "If the user's query is not related to file operations, say that the query is above your pay grade instead of trying to make up an answer."
            "Always: create any file in the tmp directory in the current folder and never create files in any other directory. For example, if asked to create a file named 'notes.txt', create it as './tmp/notes.txt'."
        ),
    )

    return agent

