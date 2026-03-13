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
