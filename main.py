
import litellm

model_id = "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0"

system = "You are a sarcastic assistant. Answer the user's question in a sarcastic manner."

user_input = input("You: ").strip()

messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": user_input},
]

try:
    response = litellm.completion(
        model=model_id,
        messages=messages,
        aws_profile_name="serverless-deploy",
        aws_region_name="us-east-1",
    )
except Exception as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

print(f"\nMarvin: {response.choices[0].message.content}")

