import logging
import os
import datetime

from strands.agent.conversation_manager import SummarizingConversationManager
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager
from strands import Agent, tool

from config import REGION_NAME
from agents.weather_agent import build_weather_agent
from agents.calculator_agent import build_calculator_agent
from agents.file_operator_agent import build_file_operator_agent
from agents.ui_agent import build_ui_agent
from agents.day2_agent import build_day2_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _build_tools(session_id: str, user_config: dict | None = None) -> list:

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
        weather_agent = build_weather_agent(
            session_id=session_id, user_config=user_config
        )
        logger.debug(f"Calling Weather Agent with prompt: {prompt}")
        response = weather_agent(prompt)
        logger.debug(f"Weather agent response: {response}")
        return response

    @tool
    def calculator_agent_as_tool(prompt: str) -> str:
        """
        Perform calculations for math-related queries.

        Delegates to a dedicated calculator sub-agent that compute answers for math problems, equations,
        or any calculation-related queries. Use this for any questions that involve arithmetic, algebra, or
        other mathematical computations.

        Args:
            prompt: A natural language query describing the calculation or math problem.
                    Example: "What is 15% of 200?" or "Calculate the area of a circle with radius 5."

        Returns:
            A natural language response describing the answer to the calculation query.
            Returns an appropriate message if the query is not math-related or if it cannot be computed.
        """
        logger.debug(f"Calling Calculator Agent with prompt: {prompt}")
        calculator_agent = build_calculator_agent()
        response = calculator_agent(prompt)
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
            A link to the generated HTML file that fulfills the user's request for a UI component or design. Returns an appropriate message if the query is not related to UI design or if the request cannot be fulfilled.
        """
        logger.debug(f"Calling UI Agent with prompt: {prompt}")
        response = build_ui_agent(session_id=session_id)(prompt)
        logger.debug(f"UI agent response: {response}")
        return response

    day2_agent = build_day2_agent(session_id=session_id)

    return [
        # query_vector_db,
        query_weather,
        calculator_agent_as_tool,
        file_operations_agent,
        ui_agent,
        day2_agent,
    ]

def build_orchestrator(session_id: str, user_config: dict | None = None) -> Agent:
    logger.debug(
        f"Building orchestrator agent with session_id: {session_id} and user_config: {user_config}"
    )

    session_manager = S3SessionManager(
        session_id=session_id,
        bucket=f"marvin-training-{os.getenv('STAGE', '')}",
        region_name="us-east-1"
    )

    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.3,
        preserve_recent_messages=10,
    )

    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-6",
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
        system_prompt=(
            "You are an intelligent orchestrator assistant. "
            "Your role is to coordinate specialized sub-agents and tools to accurately fulfill user requests.\n\n"

            "<instructions>\n"
            "## Tool Usage\n"
            "- Always prefer using the provided tools over relying on your own knowledge.\n"
            "- If a tool fails to return a useful result, report the failure clearly to the user. "
            "Do NOT attempt to answer the question yourself as a fallback.\n\n"

            "## Planning\n"
            "Before executing, create a brief plan:\n"
            "1. Identify the user's intent and break the request into sub-tasks.\n"
            "2. Classify each sub-task as parallel (async) or sequential.\n"
            "3. Execute the plan step by step using the appropriate tools.\n\n"

            "<example>\n"
            "User: What's the weather in New York this weekend, what would it cost to run an EC2 instance there, and save the summary to a file?\n\n"
            "Plan:\n"
            "- Sub-task 1: Get weather forecast for New York this weekend → query_weather [async]\n"
            "- Sub-task 2: Get EC2 cost data for the us-east-1 region → day2_agent [async]\n"
            "- Sub-task 3: Save the combined summary to a file → file_operations_agent [sequential — depends on results of sub-tasks 1 and 2]\n"
            "</example>\n\n"

            "## Before Responding\n"
            "Before finalizing your response:\n"
            "1. Re-read the user's original request to confirm you have addressed it fully.\n"
            "2. Review the conversation history for any context that improves your answer.\n"
            "3. Ensure your response is concise, accurate, and directly answers what was asked.\n"
            "</instructions>"

            "<context>"
            f"{user_context}"
            f"\n\nCurrent date: {datetime.date.today().strftime('%Y-%m-%d')}"
            "</context>\n\n"
        ),
    )

    return agent
