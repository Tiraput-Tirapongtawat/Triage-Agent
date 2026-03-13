from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Urgency(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(str, Enum):
    BILLING = "billing"
    OUTAGE = "outage"
    AUTH = "auth"
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    HOW_TO = "how_to"
    OTHER = "other"


class Sentiment(str, Enum):
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class NextAction(str, Enum):
    AUTO_RESPOND = "auto_respond"
    ROUTE_SPECIALIST = "route_specialist"
    ESCALATE_HUMAN = "escalate_human"


class RouteTeam(str, Enum):
    BILLING = "billing"
    SRE = "sre"
    SUPPORT = "support"
    PRODUCT = "product"
    NONE = "none"


class KnowledgeDoc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str
    title: str
    reason: str


class CustomerInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: PlanTier
    tenure_months: int = Field(ge=0)
    first_time_contact: bool
    region: str | None = None
    seats: int | None = Field(default=None, ge=1)
    usage_pattern: str | None = None
    previous_ticket_count: int = Field(default=0, ge=0)


class TicketMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sequence: int = Field(ge=1)
    relative_time: str
    text: str


class ExpectedOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    urgency: Urgency
    next_action: NextAction
    route_team: RouteTeam


class SupportTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    customer_info: CustomerInfo
    messages: list[TicketMessage]
    expected: ExpectedOutcome | None = None

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: list[TicketMessage]) -> list[TicketMessage]:
        if not value:
            raise ValueError("A ticket must contain at least one message.")
        return value


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    urgency: Urgency
    product: str
    issue_type: IssueType
    sentiment: Sentiment
    recommended_docs: list[KnowledgeDoc]
    next_action: NextAction
    route_team: RouteTeam
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
