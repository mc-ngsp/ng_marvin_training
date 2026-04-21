from strands import Agent, tool
from strands_tools import calculator
from strands.models import BedrockModel

from config import MODEL_ID, REGION_NAME

def build_calculator_agent(session_id: str) -> Agent:
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION_NAME,
    )

    agent = Agent(
        name="Calculator Agent",
        model=model,
        tools=[calculator],
        system_prompt=(
            "You are a helpful assistant that can perform calculations using the calculator tool."
            "Use the calculator tool for any queries that involve math or calculations."
            "If the user's query is not related to calculations, say that the query is above your pay grade instead of trying to make up an answer."
        ),
    )

    return agent