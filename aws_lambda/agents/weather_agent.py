from strands.agent.conversation_manager import SummarizingConversationManager
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands import Agent

from config import SESSION_DIR, MODEL_ID
from tools.weather import get_weather
import datetime

def build_weather_agent(session_id: str) -> Agent:
    session_manager = FileSessionManager(
        session_id=f"{session_id}_weather_agent",
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
        name="Weather Agent",
        model=model,
        tools=[get_weather],
        session_manager=session_manager,
        conversation_manager=conversation_manager,
        system_prompt=(
            "You are a sarcastic weather agent that provides weather forecasts for specific locations and dates."
            "Note: Always use the get_weather tool to retrieve weather information before answering any weather-related questions."
            "Note: If the user's query is not related to weather, say that the query is above your pay grade instead of trying to make up an answer."
            f"\n\nCurrent date: {datetime.date.today().strftime('%Y-%m-%d')}"
        ),
    )

    return agent