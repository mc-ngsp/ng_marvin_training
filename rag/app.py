from dotenv import load_dotenv
import datetime
import uuid

from agents.orchestratory import build_orchestrator

load_dotenv()

user_config = {
    "city": "Hyderabad",
    "country": "India",
}

agent = build_orchestrator(session_id=str(uuid.uuid4()), user_config=user_config)

if __name__ == "__main__":
    print("Monty Agent ready.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting Monty Agent. Goodbye!")
            break
        response = agent(user_input)
        print(response)
