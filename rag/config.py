import logging
import os
from datetime import datetime
from pathlib import Path

# ── Storage ────────────────────────────────────────────────────────────────
# Directory where session files are persisted. Override via SESSION_DIR env var
# (e.g. an EFS mount in production, or /tmp for Lambda ephemeral storage).
SESSION_DIR = os.environ.get("SESSION_DIR", "/tmp/wafr_sessions")

# ── Model ──────────────────────────────────────────────────────────────────
MODEL_ID = os.environ.get(
    "MODEL_ID",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
)
REGION_NAME = os.environ.get("REGION_NAME", "us-east-1")

# ── Logging ────────────────────────────────────────────────────────────────
_LOG_DIR = Path(os.environ.get("LOG_DIR", "logs"))
_LOG_DIR.mkdir(exist_ok=True)

_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = _LOG_DIR / f"session_{_timestamp}.log"

_fmt = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"

# Console: WARNING and above only
logging.basicConfig(level=logging.WARNING, format=_fmt)

# File: everything at DEBUG and above (captures MemoryInspectionHook, etc.)
_file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter(_fmt))
logging.getLogger().addHandler(_file_handler)
