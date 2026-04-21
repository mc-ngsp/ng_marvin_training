from strands.models import BedrockModel
from strands import Agent

from config import MODEL_ID, REGION_NAME

def build_hyde_agent() -> Agent:

    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION_NAME,
    )

    hyde_agent = Agent(
        name="HyDE Agent",
        model=model,
        system_prompt="You are a MontyCloud assistant and can answer any questions related to MontyCloud and CloudOps. Generate a detailed, factual-sounding passage that would answer the following question. Write as if it's an excerpt from a blog article.",
        callback_handler=None
    )

    return hyde_agent