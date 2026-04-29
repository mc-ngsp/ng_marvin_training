try:
    import unzip_requirements
except ImportError:
    pass

import os
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

EXPECTED_API_KEY = os.environ.get("API_KEY", "")


def authorize(event: Dict[str, Any], _context) -> Dict[str, Any]:
    headers = event.get("headers") or {}
    query_params = event.get("queryStringParameters") or {}

    api_key = (
        headers.get("x-api-key")
        or headers.get("X-Api-Key")
        or headers.get("X-API-Key")
        or query_params.get("x-api-key")
    )

    connection_arn = event["methodArn"]
    effect = "Allow" if (api_key and api_key == EXPECTED_API_KEY) else "Deny"

    logger.info(f"Authorizer result: {effect}")

    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": connection_arn,
                }
            ],
        },
    }
