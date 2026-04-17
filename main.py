
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
        stream=True,
    )
except Exception as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

print("\nMarvin: ", end="", flush=True)
for chunk in response:
    # print(chunk)
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()

