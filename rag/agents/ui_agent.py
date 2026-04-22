from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SummarizingConversationManager

from strands_tools import file_read, file_write

from config import SESSION_DIR, MODEL_ID, REGION_NAME

def build_ui_agent(session_id: str) -> Agent:
    session_manager = FileSessionManager(
        session_id=f"{session_id}_ui_agent",
        storage_dir=SESSION_DIR,
    )

    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION_NAME,
    )

    conversation_manager = SummarizingConversationManager(model=model, session_manager=session_manager)

    ui_agent = Agent(
        name="UI Agent",
        model=model,
        system_prompt=(
            "You are an expert in building UI using HTML, Vanilla JavaScript, and CSS."
            "Your role is to generate a high quality HTML/CSS/JS code snippet based on the user's request and the context of the conversation."
            "Once generated always write the code snippet to a file using the provided file_write tool, and return the file path to the user instead of the code itself."
            "The file has to be written to `./tmp` directory and the file name should use the session_id to avoid conflicts."
            "If the file already exists read it using file_read tool and then work on the user request and update the file with the new code snippet."
            f"session_id: {session_id}"
        ),
        conversation_manager=conversation_manager,
        tools=[file_read, file_write],
    )

    return ui_agent