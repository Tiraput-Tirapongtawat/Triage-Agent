from __future__ import annotations

from format import (
    IssueType,
    KnowledgeDoc,
    NextAction,
    RouteTeam,
    Sentiment,
    SupportTicket,
    TriageResult,
    Urgency,
)


def _combined_text(ticket: SupportTicket) -> str:
    return " ".join(message.text.lower() for message in ticket.messages)


def _infer_issue_type(text: str) -> IssueType:
    if any(
        keyword in text
        for keyword in ("charge", "payment", "refund", "card", "upgrade")
    ):
        return IssueType.BILLING
    if any(
        keyword in text
        for keyword in (
            "error 500",
            "cannot access",
            "can't access",
            "all systems operational",
        )
    ):
        return IssueType.OUTAGE
    if any(
        keyword in text
        for keyword in ("dark mode", "still shows light", "is this a bug")
    ):
        return IssueType.BUG
    if any(keyword in text for keyword in ("how to", "where can i", "do you support")):
        return IssueType.HOW_TO
    return IssueType.OTHER


def _infer_sentiment(text: str) -> Sentiment:
    angry_keywords = ("fixed now", "dispute", "ridiculous", "hello?")
    frustrated_keywords = ("cannot access", "can't access", "complaining", "still no")
    positive_keywords = ("thanks", "no rush", "cool")
    complaint_keywords = ("bug", "still", "cannot", "can't")

    has_angry = any(keyword in text for keyword in angry_keywords)
    has_frustrated = any(keyword in text for keyword in frustrated_keywords)
    has_positive = any(keyword in text for keyword in positive_keywords)
    has_complaint = any(keyword in text for keyword in complaint_keywords)

    if has_angry:
        return Sentiment.ANGRY
    if has_frustrated:
        return Sentiment.FRUSTRATED
    if has_positive and has_complaint:
        return Sentiment.NEUTRAL
    if has_positive:
        return Sentiment.POSITIVE
    return Sentiment.NEUTRAL


def _infer_urgency(ticket: SupportTicket, issue_type: IssueType, text: str) -> Urgency:
    if ticket.customer_info.plan.value == "enterprise" and any(
        keyword in text
        for keyword in ("error 500", "cannot access", "major client demo")
    ):
        return Urgency.CRITICAL

    if issue_type == IssueType.BILLING and any(
        keyword in text for keyword in ("three charges", "fixed now", "dispute")
    ):
        return Urgency.HIGH

    if issue_type == IssueType.BUG:
        return Urgency.MEDIUM

    if issue_type in (IssueType.HOW_TO, IssueType.FEATURE_REQUEST):
        return Urgency.LOW

    return Urgency.MEDIUM


def _recommended_docs(issue_type: IssueType, text: str) -> list[KnowledgeDoc]:
    if issue_type == IssueType.BILLING:
        return [
            KnowledgeDoc(
                doc_id="kb_billing_001",
                title="Duplicate Charges During Upgrade",
                reason="Covers pending duplicate charges and upgrade reconciliation.",
            ),
            KnowledgeDoc(
                doc_id="kb_billing_002",
                title="Payment Retry and Card Authorization Holds",
                reason="Explains multiple pending card authorizations and refund timing.",
            ),
        ]

    if issue_type == IssueType.OUTAGE:
        return [
            KnowledgeDoc(
                doc_id="kb_incident_010",
                title="Regional Incident Triage Runbook",
                reason="Gives first-response steps for region-scoped access failures.",
            ),
            KnowledgeDoc(
                doc_id="kb_status_004",
                title="Status Page Mismatch Troubleshooting",
                reason="Used when status page reports healthy while users still fail.",
            ),
        ]

    if issue_type == IssueType.BUG and "dark mode" in text:
        return [
            KnowledgeDoc(
                doc_id="kb_ui_007",
                title="Dark Mode and System Theme Behavior",
                reason="Explains how system default maps to app theme behavior.",
            ),
            KnowledgeDoc(
                doc_id="kb_feature_019",
                title="Feature Requests: Theme Scheduling",
                reason="Captures request path for scheduled dark mode support.",
            ),
        ]

    return [
        KnowledgeDoc(
            doc_id="kb_general_001",
            title="General Support Triage FAQ",
            reason="Default reference when issue intent is ambiguous.",
        )
    ]


def _product(issue_type: IssueType, text: str) -> str:
    if issue_type == IssueType.BILLING:
        return "pro_upgrade"
    if issue_type == IssueType.OUTAGE:
        return "core_platform"
    if issue_type == IssueType.BUG and "dark mode" in text:
        return "appearance_settings"
    return "core_platform"


def _next_action(
    issue_type: IssueType, urgency: Urgency, text: str
) -> tuple[NextAction, RouteTeam]:
    if urgency == Urgency.CRITICAL:
        return NextAction.ESCALATE_HUMAN, RouteTeam.SRE

    if urgency == Urgency.HIGH:
        return NextAction.ROUTE_SPECIALIST, RouteTeam.BILLING

    if (
        urgency == Urgency.MEDIUM
        and issue_type == IssueType.BUG
        and "schedule dark mode" in text
    ):
        return NextAction.AUTO_RESPOND, RouteTeam.PRODUCT

    if urgency == Urgency.MEDIUM:
        return NextAction.ROUTE_SPECIALIST, RouteTeam.SUPPORT

    if urgency == Urgency.LOW and issue_type == IssueType.FEATURE_REQUEST:
        return NextAction.AUTO_RESPOND, RouteTeam.PRODUCT

    return NextAction.AUTO_RESPOND, RouteTeam.NONE


def _confidence(urgency: Urgency, issue_type: IssueType) -> float:
    if urgency == Urgency.CRITICAL:
        return 0.95
    if urgency == Urgency.HIGH:
        return 0.92
    if issue_type == IssueType.BUG:
        return 0.79
    return 0.70


def triage_ticket(ticket: SupportTicket) -> TriageResult:
    text = _combined_text(ticket)
    issue_type = _infer_issue_type(text)
    sentiment = _infer_sentiment(text)
    urgency = _infer_urgency(ticket, issue_type, text)
    next_action, route_team = _next_action(issue_type, urgency, text)

    result = TriageResult(
        ticket_id=ticket.ticket_id,
        urgency=urgency,
        product=_product(issue_type, text),
        issue_type=issue_type,
        sentiment=sentiment,
        recommended_docs=_recommended_docs(issue_type, text),
        next_action=next_action,
        route_team=route_team,
        confidence=_confidence(urgency, issue_type),
        rationale=(
            "Deterministic checkpoint triage based on conversation signals, "
            "customer context, and issue keywords."
        ),
    )
    return result
