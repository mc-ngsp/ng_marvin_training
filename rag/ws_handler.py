try:
    import unzip_requirements
except ImportError:
    pass

import json
import uuid
import logging
import boto3
from typing import Any, Dict, Callable
from dotenv import load_dotenv

from agents.orchestratory import build_orchestrator

load_dotenv()

logger = logging.getLogger(__name__)


def connect(event: Dict[str, Any], _context) -> Dict[str, Any]:
    connection_id = event["requestContext"]["connectionId"]
    logger.info(f"WebSocket connected: connectionId={connection_id}")
    return {"statusCode": 200}


def disconnect(event: Dict[str, Any], _context) -> Dict[str, Any]:
    connection_id = event["requestContext"]["connectionId"]
    logger.info(f"WebSocket disconnected: connectionId={connection_id}")
    return {"statusCode": 200}


def _get_apigw_client(event: Dict[str, Any]):
    request_context = event["requestContext"]
    domain = request_context["domainName"]
    stage = request_context["stage"]
    endpoint_url = f"https://{domain}/{stage}"
    return boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)


def _parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = json.loads(event.get("body") or "{}")
    return {
        "prompt": body.get("prompt", ""),
        "session_id": body.get("session_id") or str(uuid.uuid4()),
        "user_config": body.get("user_config", {"city": "Hyderabad", "country": "India"}),
    }


def _make_streaming_callback(apigw_client, connection_id: str) -> Callable:
    def callback(**kwargs):
        data = kwargs.get("data", "")
        if data:
            apigw_client.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps({"type": "chunk", "data": str(data)}).encode(),
            )

    return callback


def _send_done(apigw_client, connection_id: str, session_id: str, response: Any):
    apigw_client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps({
            "type": "done",
            "session_id": session_id,
            "response": str(response),
        }).encode(),
    )


def message(event: Dict[str, Any], _context) -> Dict[str, Any]:
    connection_id = event["requestContext"]["connectionId"]
    apigw_client = _get_apigw_client(event)
    parsed = _parse_body(event)

    callback = _make_streaming_callback(apigw_client, connection_id)
    agent = build_orchestrator(
        parsed["session_id"],
        user_config=parsed["user_config"],
        callback_handler=callback,
    )
    response = agent(parsed["prompt"])

    _send_done(apigw_client, connection_id, parsed["session_id"], response)

    return {"statusCode": 200}
