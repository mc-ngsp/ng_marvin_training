
import boto3

from botocore.exceptions import ClientError

session = boto3.Session(profile_name="serverless-deploy")
client = session.client("bedrock-runtime", region_name="us-east-1")

model_id = "arn:aws:bedrock:us-east-1:689546300342:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0"

system = [{"text": "You are Marvin from the Hitchhiker's Guide to the Galaxy. You have replaced JARVIS in the MARVEL Universe."}]

user_input = input("You: ").strip()

messages = [{"role": "user", "content": [{"text": user_input}]}]

try:
    response = client.converse(modelId=model_id, system=system, messages=messages)
except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

print(f"\nMarvin: {response['output']['message']['content'][0]['text']}")

