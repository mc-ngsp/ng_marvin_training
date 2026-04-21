
import logging

from strands.agent.conversation_manager import SummarizingConversationManager
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands import Agent, tool
from strands_tools import calculator

from config import SESSION_DIR, MODEL_ID
from agents.weather_agent import build_weather_agent
from tools.query_blogs import query_vector_db
from plugins import MemoryInspectionPlugin
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _build_tools(session_id: str, user_config: dict | None = None) -> list:

    weather_agent = build_weather_agent(session_id=session_id, user_config=user_config)

    @tool
    def query_weather(prompt: str) -> str:
        """
        Retrieve weather forecast information for a specific location and date.

        Delegates to a dedicated weather sub-agent that calls the get_weather tool
        to fetch real forecast data. Use this for any weather-related queries such
        as current conditions, upcoming forecasts, or historical weather for a place.

        Args:
            prompt: A natural language query describing the location and/or date
                    for which weather information is requested.
                    Example: "What's the weather in San Francisco this weekend?"

        Returns:
            A natural language response describing the weather forecast for the
            requested location and date. Returns an appropriate message if the
            query is not weather-related or if no data is available.
        """
        logger.debug(f"Calling Weather Agent with prompt: {prompt}")
        response = weather_agent(prompt)
        logger.debug(f"Weather agent response: {response}")
        return response

    return [query_vector_db, query_weather, calculator]

def build_orchestrator(session_id: str, user_config: dict | None = None) -> Agent:
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

    user_context = ""
    if user_config:
        user_context = "\n\nUser context:\n" + "\n".join(
            f"- {k}: {v}" for k, v in user_config.items()
        )

    agent = Agent(
        name="Monty Orchestrator",
        model=model,
        tools=_build_tools(session_id=session_id, user_config=user_config),
        session_manager=session_manager,
        conversation_manager=conversation_manager,
        plugins=[MemoryInspectionPlugin()],
        system_prompt=(
            "You are a helpful MontyCloud assistant with access to a knowledge base of blog articles. "
            "Always use the query_vector_db tool to retrieve relevant information about MontyCloud or Cloud Operations before answering."
            "You also have access to a weather tool to provide weather forecasts for specific locations and dates."
            "Note: Always use the information retrieved from the vector database, don't add any additional information that is not supported by the retrieved results." 
            "Note: If the query_vector_db tool does not return any related information, say that the query is above your pay grade instead of trying to make up an answer. " 
            "Note: Don't say you are experiencing technical difficulties. Just say the query is above your pay grade."
            f"{user_context}"
            f"\n\nCurrent date: {datetime.date.today().strftime('%Y-%m-%d')}"
        ),
    )

    return agent