from strands import Agent
from strands.models import BedrockModel

from config import SESSION_DIR, MODEL_ID, REGION_NAME
from tools.write_file import write_to_s3
from tools.read_file import read_from_s3

def build_ui_agent(session_id: str) -> Agent:
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION_NAME,
    )

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
            f"1. Check if a file for this session already exists in S3 with key `{session_id}.html`.\n"
            "   - If it exists: read it using `read_from_s3`, then modify it to fulfill the user's request.\n"
            "   - If it does not exist: generate the full code from scratch.\n"
            f"2. Write the final code to S3 with key `{session_id}.html` using `write_to_s3`.\n"
            "3. Always return the S3 file URL to the user — never return the raw code in the response.\n\n"

            "## Output Rules\n"
            "- Always use the `write_to_s3` tool to persist the code; never skip this step.\n"
            "- Your response to the user must contain the S3 file URL, not the code itself.\n"
            "- Produce clean, semantic, and well-commented code.\n"
            "</instructions>\n\n"

            f"<context>\nsession_id: {session_id}\n</context>"
        ),
        # conversation_manager=conversation_manager,
        tools=[read_from_s3, write_to_s3],
    )

    return ui_agent