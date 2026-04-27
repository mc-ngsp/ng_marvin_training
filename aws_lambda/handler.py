import json
import logging
import uuid
from typing import Any, Dict

from agents.weather_agent import build_weather_agent

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any], _context) -> Dict[str, Any]:
    # Support both direct invocation and API Gateway HTTP API (payload v2)
    if "requestContext" in event:
        body = json.loads(event.get("body") or "{}")
        session_id = body.get("session_id") or str(uuid.uuid4())
        prompt = body.get("prompt")
    else:
        session_id = event.get("session_id") or str(uuid.uuid4())
        prompt = event.get("prompt")

    agent = build_weather_agent(session_id)
    response = agent(prompt)

    result = {"session_id": session_id, "response": str(response)}

    if "requestContext" in event:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }

    return result
