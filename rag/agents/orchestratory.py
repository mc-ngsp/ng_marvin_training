
import logging

from strands.agent.conversation_manager import SummarizingConversationManager
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands import Agent, tool

from config import SESSION_DIR, MODEL_ID, REGION_NAME
from agents.weather_agent import build_weather_agent
from agents.calculator_agent import build_calculator_agent
from agents.file_operator_agent import build_file_operator_agent
from agents.ui_agent import build_ui_agent
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

    # calculator_agent = build_calculator_agent(session_id=session_id)
    def calculator_agent(prompt: str) -> str:
        """
        Perform calculations for math-related queries.

        Delegates to a dedicated calculator sub-agent that calls the calculator tool
        to compute answers for math problems, equations, or any calculation-related
        queries. Use this for any questions that involve arithmetic, algebra, or
        other mathematical computations.

        Args:
            prompt: A natural language query describing the calculation or math problem.
                    Example: "What is 15% of 200?" or "Calculate the area of a circle with radius 5."

        Returns:
            A natural language response describing the answer to the calculation query.
            Returns an appropriate message if the query is not math-related or if it cannot be computed.
        """
        logger.debug(f"Calling Calculator Agent with prompt: {prompt}")
        response = build_calculator_agent(session_id=session_id)(prompt)
        logger.debug(f"Calculator agent response: {response}")
        return response

    @tool
    def file_operations_agent(prompt: str) -> str:
        """
        Perform file read/write operations based on user queries.

        Delegates to a dedicated file operator sub-agent that calls the file_read and file_write tools
        to handle any queries related to reading from or writing to files. Use this for any questions
        that involve accessing file contents, saving information to files, or modifying files.

        Args:
            prompt: A natural language query describing the desired file operation.
                    Example: "Read the contents of report.txt" or "Write 'Hello World' to greeting.txt"

        Returns:
            A natural language response describing the result of the file operation.
            Returns an appropriate message if the query is not related to file operations or if the operation fails.
        """
        logger.debug(f"Calling File Operator Agent with prompt: {prompt}")
        response = build_file_operator_agent(session_id=session_id)(prompt)
        logger.debug(f"File Operator agent response: {response}")
        return response

    @tool
    def ui_agent(prompt: str) -> str:
        """
        Generate HTML/CSS/JS code snippets based on user requests for UI components.

        Delegates to a dedicated UI sub-agent that specializes in building user interfaces using HTML, CSS, and JavaScript.
        Use this for any queries where the user is asking for help creating or designing UI elements, such as "Create a responsive navbar" or "How do I make a button with a hover effect?"

        Args:
            prompt: A natural language query describing the desired UI component or design.
                    Example: "Generate HTML/CSS code for a login form" or "How can I create a grid layout with CSS?"

        Returns:
            A html/CSS/JS code snippet that fulfills the user's request for a UI component or design. Returns an appropriate message if the query is not related to UI design or if the request cannot be fulfilled.
        """
        logger.debug(f"Calling UI Agent with prompt: {prompt}")
        response = build_ui_agent(session_id=session_id)(prompt)
        logger.debug(f"UI agent response: {response}")
        return response

    return [query_vector_db, query_weather, calculator_agent, file_operations_agent, ui_agent]

def build_orchestrator(session_id: str, user_config: dict | None = None) -> Agent:
    logger.debug(f"Building orchestrator agent with session_id: {session_id} and user_config: {user_config}")
    session_manager = FileSessionManager(
        session_id=f"{session_id}_orchestrator",
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