import logging
import os
from datetime import datetime
from pathlib import Path

# ── Storage ────────────────────────────────────────────────────────────────
# Directory where session files are persisted. Override via SESSION_DIR env var
# (e.g. an EFS mount in production, or /tmp for Lambda ephemeral storage).
SESSION_DIR = os.environ.get("SESSION_DIR", "/tmp/wather_agent_sessions")

# ── Model ──────────────────────────────────────────────────────────────────
MODEL_ID = os.environ.get(
    "MODEL_ID",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
)
REGION_NAME = os.environ.get("REGION_NAME", "us-east-1")
