from __future__ import annotations

from fixtures import load_sample_tickets


def _build_ticket_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for ticket in load_sample_tickets():
        plan = ticket.customer_info.plan.value
        region = (ticket.customer_info.region or "global").lower()
        risk_flags: list[str] = []

        if plan == "enterprise":
            risk_flags.append("revenue_risk")
        if ticket.customer_info.previous_ticket_count >= 10:
            risk_flags.append("support_load_high")
        if ticket.customer_info.first_time_contact:
            risk_flags.append("first_time_contact")

        index[ticket.ticket_id] = {
            "plan": plan,
            "tenure_months": ticket.customer_info.tenure_months,
            "region": region,
            "seats": ticket.customer_info.seats,
            "previous_ticket_count": ticket.customer_info.previous_ticket_count,
            "risk_flags": risk_flags,
        }
    return index


TICKET_INDEX = _build_ticket_index()

KB_DOCS = {
    "billing": [
        {
            "doc_id": "kb_billing_001",
            "title": "Duplicate Charges During Upgrade",
            "reason": "Covers duplicate pending charges and entitlement mismatch.",
        },
        {
            "doc_id": "kb_billing_002",
            "title": "Card Authorization Hold Timeline",
            "reason": "Explains pending holds, settlement, and reversal timing.",
        },
    ],
    "outage": [
        {
            "doc_id": "kb_incident_010",
            "title": "Regional Incident Triage Runbook",
            "reason": "First-response workflow for region-specific outages.",
        },
        {
            "doc_id": "kb_status_004",
            "title": "Status Page Mismatch Troubleshooting",
            "reason": "Guidance when status page is green but users fail.",
        },
    ],
    "theme": [
        {
            "doc_id": "kb_ui_007",
            "title": "Dark Mode and System Theme Behavior",
            "reason": "Explains light/system/dark rendering behavior and caveats.",
        },
        {
            "doc_id": "kb_feature_019",
            "title": "Feature Request Intake: Theme Scheduling",
            "reason": "How to route scheduling requests to product feedback queue.",
        },
    ],
    "general": [
        {
            "doc_id": "kb_general_001",
            "title": "General Support FAQ",
            "reason": "Default troubleshooting and escalation playbook.",
        }
    ],
}


def customer_history_lookup(ticket_id: str) -> dict:
    """Lookup customer history context by ticket_id.

    Use this before final triage to validate business impact and risk flags.
    """
    return TICKET_INDEX.get(
        ticket_id,
        {
            "plan": "unknown",
            "tenure_months": 0,
            "region": "global",
            "seats": None,
            "previous_ticket_count": 0,
            "risk_flags": ["missing_customer_record"],
        },
    )


def knowledge_base_lookup(issue_hint: str, language: str = "en") -> list[dict]:
    """Lookup related knowledge-base docs using issue_hint text.

    Return top relevant docs for the agent to cite in recommended_docs.
    """
    hint = issue_hint.lower()
    docs: list[dict] = []

    if any(token in hint for token in ("charge", "payment", "refund", "invoice", "billing")):
        docs.extend(KB_DOCS["billing"])
    if any(token in hint for token in ("error 500", "outage", "cannot access", "region", "status page")):
        docs.extend(KB_DOCS["outage"])
    if any(token in hint for token in ("dark mode", "theme", "appearance")):
        docs.extend(KB_DOCS["theme"])

    if not docs:
        docs = KB_DOCS["general"]

    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique_docs: list[dict] = []
    for doc in docs:
        doc_id = doc["doc_id"]
        if doc_id in seen:
            continue
        seen.add(doc_id)
        unique_docs.append(doc)

    return unique_docs[:3]


def system_status_lookup(region: str) -> dict:
    """Check mocked system health for a region."""
    normalized = region.lower().strip()
    if normalized in {"thailand", "asia", "apac"}:
        return {
            "region": normalized,
            "status": "degraded",
            "incident_id": "inc_asia_2026_0312_mock",
            "message": "Intermittent authentication and API gateway errors in Asia cluster.",
        }
    return {
        "region": normalized or "global",
        "status": "operational",
        "incident_id": None,
        "message": "No active incidents in this region.",
    }


AGENT_TOOLS = [customer_history_lookup, knowledge_base_lookup, system_status_lookup]
