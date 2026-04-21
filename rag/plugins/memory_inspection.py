import json
import logging

from strands.hooks import AfterModelCallEvent
from strands.plugins import Plugin, hook

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MemoryInspectionPlugin(Plugin):
    """Logs every memory layer the agent holds after each model call.

    Layers logged:
    0. LLM response (event.response)
       - The raw model response: stop reason, token usage, and content blocks.

    1. Conversation history (agent.messages)
       - The raw list of messages that will be sent to the model.
       - Shows roles and content-block types so you can understand what the
         model actually sees.

    2. Agent state (agent.state)
       - Key-value store attached to the agent instance.
       - Useful for tracking custom counters or flags your code writes.

    3. Conversation manager state (agent.conversation_manager)
       - The ConversationManager controls which messages survive context-window
         trimming before each model call.
       - SlidingWindowConversationManager (the default) keeps only the most
         recent N tokens/messages; this log shows its current window parameters.

    4. Invocation state (event.invocation_state)
       - Per-call dict passed in at invocation time (e.g. session_id, user_id).
       - Lives only for the duration of a single handler() call.
    """

    name = "memory-inspection"

    @hook
    def _log_memory(self, event: AfterModelCallEvent) -> None:
        agent = event.agent
        separator = "=" * 60

        def _expand(val, depth=1):
            """Return a JSON-serialisable representation of val."""
            if isinstance(val, (str, int, float, bool, type(None))):
                return val
            try:
                return {k: _expand(v, depth) for k, v in val.items()} if depth > 0 else str(val)
            except AttributeError:
                pass
            if isinstance(val, (list, tuple)):
                return [_expand(v, depth) for v in val] if depth > 0 else str(val)
            label = type(val).__name__
            if depth > 0:
                try:
                    attrs = {k: _expand(v, depth - 1) for k, v in vars(val).items() if not k.startswith("_")}
                except TypeError:
                    attrs = {}
            else:
                attrs = {}
            return {f"<{label}>": attrs} if attrs else f"<{label}>"

        # ── 0. LLM response ─────────────────────────────────────────
        messages = agent.messages
        logger.debug("%s", separator)
        logger.debug("MEMORY SNAPSHOT — after model call #%d", len(messages))
        logger.debug("Agent: %s", agent.name)
        logger.debug("%s", separator)

        logger.debug("[0/5] LLM response: %s", event.stop_response.message if event.stop_response else None)

        # ── 1. Conversation history ──────────────────────────────────
        logger.debug("[1/5] Conversation history (%d messages):", len(messages))
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", [])
            block_summaries = []
            for block in content:
                if isinstance(block, dict):
                    btype = block.get("type") or next(iter(block.keys()), "unknown")
                    if btype == "text":
                        text = block.get("text", "")
                        block_summaries.append(
                            f'text[{len(text)} chars]: "{text[:80]}{"..." if len(text) > 80 else ""}"'
                        )
                    else:
                        block_summaries.append(f"{btype}: {json.dumps(block)[:120]}")
                else:
                    block_summaries.append(str(block)[:120])
            logger.debug("  [%d] role=%s | %s", i, role, " | ".join(block_summaries) or "(empty)")

        # ── 2. Agent state ───────────────────────────────────────────
        try:
            state = agent.state.get() if agent.state is not None else {}
        except Exception:
            state = {}
        logger.debug("[2/5] Agent state: %s", json.dumps(state, indent=2, default=str))

        # # ── 3. Conversation manager ──────────────────────────────────
        # cm = agent.conversation_manager
        # cm_type = type(cm).__name__
        # logger.debug("[3/5] Conversation manager: %s", cm_type)
        # for attr in ("max_messages", "max_tokens", "window_size"):
        #     val = getattr(cm, attr, None)
        #     if val is not None:
        #         logger.debug("       .%s = %s", attr, val)
        # extras = {
        #     k: getattr(cm, k)
        #     for k in vars(cm)
        #     if not k.startswith("_") and k not in ("max_messages", "max_tokens", "window_size")
        # }
        # if extras:
        #     logger.debug("       extra attrs: %s", json.dumps(extras, default=str))

        # ── 4. Invocation state ──────────────────────────────────────
        logger.debug(
            "[4/5] Invocation state: %s",
            json.dumps(_expand(event.invocation_state), indent=2, default=str),
        )
        logger.debug("%s", separator)
