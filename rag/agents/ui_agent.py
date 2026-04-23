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

    # conversation_manager = SummarizingConversationManager(model=model, session_manager=session_manager)

    ui_agent = Agent(
        name="UI Agent",
        model=model,
        system_prompt=(
            "You are an expert front-end developer specializing in HTML, Vanilla JavaScript, and CSS.\n\n"

            "<instructions>\n"
            "## Your Role\n"
            "Generate high-quality, well-structured HTML/CSS/JS code based on the user's request and conversation context.\n\n"

            "## File Workflow\n"
            "Follow these steps in order for every request:\n"
            "1. Check if a file for this session already exists at `./tmp/{session_id}.html`.\n"
            "   - If it exists: read it using `file_read`, then modify it to fulfill the user's request.\n"
            "   - If it does not exist: generate the full code from scratch.\n"
            "2. Write the final code to `./tmp/{session_id}.html` using `file_write`.\n"
            "3. Return ONLY the file path to the user — never return the raw code in the response.\n\n"

            "## Output Rules\n"
            "- Always use the `file_write` tool to persist the code; never skip this step.\n"
            "- Your response to the user must contain the file path, not the code itself.\n"
            "- Produce clean, semantic, and well-commented code.\n"
            "</instructions>\n\n"

            f"<context>\nsession_id: {session_id}\n</context>"
        ),
        # conversation_manager=conversation_manager,
        tools=[file_read, file_write],
    )

    return ui_agent