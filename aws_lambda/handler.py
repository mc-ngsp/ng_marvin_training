import logging
import uuid
from typing import Any, Dict

from agents.weather_agent import build_weather_agent

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any], _context) -> Dict[str, Any]:
    session_id = event.get("session_id") or str(uuid.uuid4())
    agent = build_weather_agent(session_id)
    response = agent(event.get("prompt"))

    return {
        "session_id": session_id,
        "response": str(response),
    }
