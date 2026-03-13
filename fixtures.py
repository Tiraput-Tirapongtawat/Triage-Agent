from __future__ import annotations

from format import SupportTicket


SAMPLE_TICKETS_RAW = [
    {
        "ticket_id": "ticket_001_billing_duplicate_charge",
        "customer_info": {
            "plan": "free",
            "tenure_months": 4,
            "first_time_contact": True,
            "region": "global",
            "previous_ticket_count": 0,
        },
        "messages": [
            {
                "sequence": 1,
                "relative_time": "3 hours ago",
                "text": "My payment failed when I tried to upgrade to Pro. Can you check what's wrong?",
            },
            {
                "sequence": 2,
                "relative_time": "2 hours ago",
                "text": "I tried again with a different card. Now I see two pending charges but my account still shows Free plan.",
            },
            {
                "sequence": 3,
                "relative_time": "1 hour ago",
                "text": "I now have three charges of $29.99 and still no Pro access.",
            },
            {
                "sequence": 4,
                "relative_time": "just now",
                "text": "Hello? I need this fixed now. If these charges are not reversed by end of day I will dispute all of them with my bank.",
            },
        ],
        "expected": {
            "urgency": "high",
            "next_action": "route_specialist",
            "route_team": "billing",
        },
    },
    {
        "ticket_id": "ticket_002_enterprise_error_500_asia",
        "customer_info": {
            "plan": "enterprise",
            "tenure_months": 8,
            "first_time_contact": True,
            "region": "thailand",
            "seats": 45,
            "previous_ticket_count": 0,
        },
        "messages": [
            {
                "sequence": 1,
                "relative_time": "2 hours ago",
                "text": "[Thai translated] We cannot access the system and it shows error 500.",
            },
            {
                "sequence": 2,
                "relative_time": "1.5 hours ago",
                "text": "[Thai translated] We tried multiple devices and browsers. Coworkers also cannot access.",
            },
            {
                "sequence": 3,
                "relative_time": "45 minutes ago",
                "text": "[Thai translated] Customers are complaining heavily and we have a major client demo this afternoon.",
            },
            {
                "sequence": 4,
                "relative_time": "just now",
                "text": "[Thai translated] status.company.com says all systems operational, but Asia region users still cannot use the product.",
            },
        ],
        "expected": {
            "urgency": "critical",
            "next_action": "escalate_human",
            "route_team": "sre",
        },
    },
    {
        "ticket_id": "ticket_003_dark_mode_bug_feature_request",
        "customer_info": {
            "plan": "pro",
            "tenure_months": 5,
            "first_time_contact": True,
            "region": "global",
            "usage_pattern": "daily_logins",
            "previous_ticket_count": 0,
        },
        "messages": [
            {
                "sequence": 1,
                "relative_time": "2 days ago",
                "text": "Do you support dark mode? No rush.",
            },
            {
                "sequence": 2,
                "relative_time": "1 day ago",
                "text": "Thanks. I found Settings > Appearance, but I only see Light and System Default. No dark mode toggle.",
            },
            {
                "sequence": 3,
                "relative_time": "1 day ago + 3 hours",
                "text": "My Mac is set to dark mode and your app still shows light theme. Is this a bug?",
            },
            {
                "sequence": 4,
                "relative_time": "today",
                "text": "Is there a way to schedule dark mode, for example auto-switch at 6pm? That would be cool.",
            },
        ],
        "expected": {
            "urgency": "medium",
            "next_action": "auto_respond",
            "route_team": "product",
        },
    },
    {
        "ticket_id": "ticket_004_how_to_export_pdf_no_expected",
        "customer_info": {
            "plan": "pro",
            "tenure_months": 2,
            "first_time_contact": False,
            "region": "global",
            "previous_ticket_count": 1,
        },
        "messages": [
            {
                "sequence": 1,
                "relative_time": "today",
                "text": "How to export a report to PDF in Pro plan?",
            }
        ],
    },
    {
        "ticket_id": "ticket_014_payment_failure",
        "customer_info": {
            "plan": "enterprise",
            "tenure_months": 36,
            "first_time_contact": False,
            "region": "apac",
            "previous_ticket_count": 14,
        },
        "messages": [
            {
                "sequence": 1,
                "relative_time": "2 hours ago",
                "text": "Our automated billing system failed to process invoices this morning.",
            },
            {
                "sequence": 2,
                "relative_time": "1 hour ago",
                "text": "We tried generating invoices manually but the system throws error code INV-443.",
            },
            {
                "sequence": 3,
                "relative_time": "20 minutes ago",
                "text": "This is affecting our entire finance workflow. We have 120+ invoices pending.",
            },
            {
                "sequence": 4,
                "relative_time": "5 minutes ago",
                "text": "If this isn't resolved soon we may miss our client billing cycle.",
            },
        ],
    },
]


def load_sample_tickets() -> list[SupportTicket]:
    return [SupportTicket.model_validate(ticket) for ticket in SAMPLE_TICKETS_RAW]
