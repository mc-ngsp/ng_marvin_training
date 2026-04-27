try:
  import unzip_requirements
except ImportError:
  pass

from dotenv import load_dotenv
from typing import Any, Dict
import logging
import uuid

from agents.orchestratory import build_orchestrator

load_dotenv()

logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any], _context) -> Dict[str, Any]:
    user_config = {
        "city": "Hyderabad",
        "country": "India",
    }
    session_id = event.get("session_id") or str(uuid.uuid4())

    agent = build_orchestrator(session_id, user_config=user_config)
    response = agent(event.get("prompt"))

    return {
        "session_id": session_id,
        "response": str(response),
    }
