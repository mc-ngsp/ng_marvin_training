from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SummarizingConversationManager
from config import SESSION_DIR, MODEL_ID, REGION_NAME
from tools.write_file import write_to_s3
from tools.read_file import read_from_s3

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
        tools=[read_from_s3, write_to_s3],
        session_manager=session_manager,
        conversation_manager=conversation_manager,
        system_prompt=(
            "You are a helpful assistant that can read from and write to S3 using the read_from_s3 and write_to_s3 tools."
            "Use the read_from_s3 tool to read the contents of a file from S3 when the user asks to see what's inside a file."
            "Use the write_to_s3 tool to write content to S3 when the user asks you to save some information."
            "After every write operation, always return the S3 file URL of the written object."
            "If the user's query is not related to S3 file operations, say that the query is above your pay grade instead of trying to make up an answer."
        ),
    )

    return agent

