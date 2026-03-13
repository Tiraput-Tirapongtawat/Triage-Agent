# Support Ticket Triage Agent

## Checkpoint 1
- Triage policy and output contract:
  - `docs/triage_policy.md`

## Checkpoint 2
- Structured schemas:
  - `format.py`
- Sample fixtures (3 provided tickets):
  - `fixtures.py`
- Deterministic mock triage engine for validation:
  - `triage_engine.py`
- AI tool-calling agent:
  - `ai_agent.py`
- Tool definitions (mock implementations):
  - `agent_tools.py`
- System prompt:
  - `docs/system_prompt.md`
- Brief write-up:
  - `docs/writeup.md`

## Run mock mode (offline)

```bash
python3 main.py --mode mock
```

Expected:
- The script loads tickets from `fixtures.py`.
- Each ticket emits schema-validated triage JSON.
- Summary shows pass/fail against expected urgency, next action, and route team.

## Run AI mode (OpenAI)
1. Add `.env` in project root:
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```
2. Run:
```bash
python3 main.py --mode ai
```

Optional:
- Run one ticket only:
```bash
python3 main.py --mode ai --ticket-id ticket_001_billing_duplicate_charge
```

## Add your own ticket
1. Open `fixtures.py`.
2. Add a new item to `SAMPLE_TICKETS_RAW`.
3. Follow the same schema used by `SupportTicket` in `format.py`.

Example:

```python
{
    "ticket_id": "ticket_999_custom_issue",
    "customer_info": {
        "plan": "pro",
        "tenure_months": 12,
        "first_time_contact": False,
        "region": "global",
        "previous_ticket_count": 2,
    },
    "messages": [
        {
            "sequence": 1,
            "relative_time": "10 minutes ago",
            "text": "I cannot log in after resetting my password.",
        },
        {
            "sequence": 2,
            "relative_time": "just now",
            "text": "This is blocking my work for today.",
        },
    ],
    "expected": {
        "urgency": "high",
        "next_action": "route_specialist",
        "route_team": "support",
    },
}
```

Notes:
- `ticket_id`, `customer_info`, and `messages` are required.
- `expected` is optional. Add it when you want pass/fail validation in `mock` mode.
- `messages` must contain at least one message.
- Use increasing `sequence` values: `1`, `2`, `3`, ...

Run only your new ticket:

```bash
python3 main.py --mode mock --ticket-id ticket_999_custom_issue
```

Or test it with the AI agent:

```bash
python3 main.py --mode ai --ticket-id ticket_999_custom_issue
```

If your ticket introduces a brand new pattern or issue category, you may also need to update:
- `triage_engine.py` for deterministic keyword/routing logic
- `agent_tools.py` for mock KB or system/tool data
- `docs/triage_policy.md` and `docs/system_prompt.md` for policy/prompt alignment
