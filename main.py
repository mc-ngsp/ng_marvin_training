from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
load_dotenv()

model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

llm = ChatBedrockConverse(
    model=model_id,
    temperature=0.7,
    region_name="us-east-1",
)

system = (
    "You are a sarcastic assistant. Answer the user's question in a sarcastic manner."
)

user_input = input("You: ").strip()

messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": user_input},
]

final_response = ""
final_metrics = ""

for chunk in llm.stream(messages):
    print(chunk)
    # print(chunk.text)
    if chunk.response_metadata.get('stopReason') is None:
        final_response += chunk.text

    if chunk.response_metadata.get('metrics') is not None:
        final_metrics = chunk.usage_metadata

print("Final response:", final_response)
print("Final metrics:", final_metrics)
