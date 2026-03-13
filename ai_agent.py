from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent

from agent_tools import AGENT_TOOLS
from format import SupportTicket, TriageResult


load_dotenv()

SYSTEM_PROMPT_PATH = Path(__file__).parent / "docs" / "system_prompt.md"
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()

_AGENT = None


def _normalize_model_name(model_name: str) -> str:
    if ":" in model_name:
        return model_name
    return f"openai:{model_name}"


def _build_agent():
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    debug = os.getenv("AGENT_DEBUG", "").lower() in {"1", "true", "yes"}
    return create_agent(
        model=_normalize_model_name(model_name),
        tools=AGENT_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        response_format=TriageResult,
        debug=debug,
    )


def _get_agent():
    global _AGENT
    if _AGENT is None:
        _AGENT = _build_agent()
    return _AGENT


def _ticket_message(ticket: SupportTicket) -> str:
    ticket_payload = ticket.model_dump(exclude={"expected": True})
    return (
        "Process this support ticket and return the final triage result.\n\n"
        f"Ticket JSON:\n{ticket_payload}"
    )


def _ensure_openai_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. Add it to .env before running --mode ai."
        )


def triage_ticket_with_ai(ticket: SupportTicket) -> TriageResult:
    _ensure_openai_key()
    agent = _get_agent()

    result_state = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": _ticket_message(ticket),
                }
            ]
        }
    )

    structured = result_state.get("structured_response")
    if structured is None:
        raise RuntimeError(
            "AI agent did not return structured_response. "
            "Check prompt/tool behavior and model compatibility."
        )

    triage = (
        structured
        if isinstance(structured, TriageResult)
        else TriageResult.model_validate(structured)
    )

    # Keep ticket id stable even if the model omits/rewrites it.
    if triage.ticket_id != ticket.ticket_id:
        triage = triage.model_copy(update={"ticket_id": ticket.ticket_id})
    return triage
