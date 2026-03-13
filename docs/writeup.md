# Brief Write-up (1 page)

## 1) Architecture decisions and why
This project is designed around a strict input/output contract and two execution modes:

- `format.py` defines `SupportTicket` and `TriageResult` with Pydantic.  
  Why: schema validation keeps outputs consistent (`urgency`, `issue_type`, `next_action`, etc.) and reduces downstream integration errors.
- `main.py` is the runner/orchestrator with `--mode mock|ai`.  
  Why: `mock` mode gives deterministic local testing; `ai` mode exercises real model + tools with the same output contract.
- `ai_agent.py` uses LangChain `create_agent` with structured response (`TriageResult`).  
  Why: tool-calling + structured output forces the model into decision-oriented responses rather than free-form text.
- `agent_tools.py` contains three tools:
  1. `customer_history_lookup`
  2. `knowledge_base_lookup`
  3. `system_status_lookup`
  Why: this matches the assignment requirement (>=2 tools) and separates business context, knowledge retrieval, and operational status checks.
- `docs/system_prompt.md` centralizes policy for urgency/action/tool usage.  
  Why: easier to audit and iterate prompt behavior without changing core code.
- `fixtures.py` includes provided sample tickets and expected outcomes (where applicable).  
  Why: regression checks are fast and explicit.

Overall design principle: keep triage deterministic at the interface level (schema + action taxonomy), while allowing model flexibility in reasoning and evidence usage.

## 2) What could go wrong and how to handle it
- **Model misclassification (urgency too low/high)**  
  Mitigation: confidence threshold + hard safety rules (e.g., enterprise outage keywords force escalation path).
- **Tool output mismatch or stale KB**  
  Mitigation: require `recommended_docs` from tool responses only; version/owner KB sources; add tool health checks.
- **Prompt injection in ticket text**  
  Mitigation: system prompt enforces role boundaries; never execute arbitrary instructions from user messages as code/actions.
- **Missing/partial customer context**  
  Mitigation: tools return safe defaults and risk flags (`missing_customer_record`), plus reduced confidence and conservative routing.
- **Language ambiguity (EN/TH mix)**  
  Mitigation: keep taxonomy in English; preserve customer-facing rationale style by language policy.
- **Cost/latency spikes**  
  Mitigation: route only high-impact tickets to full AI mode, cache repeated lookups, and monitor p95 latency/token usage.
- **Operational failures (API key/quota/network)**  
  Mitigation: explicit errors in runner, fallback to `mock` mode for continuity during incidents.

## 3) How to evaluate in production
Evaluation should combine offline quality, online reliability, and business outcomes.

### Offline (pre-deploy)
- Build a labeled benchmark set (urgency, issue_type, next_action, route_team).
- Metrics:
  - Accuracy/F1 for `urgency`
  - Accuracy for `next_action` and `route_team`
  - Schema-valid response rate
  - Tool-call correctness (did it call required tools?)
- Include multilingual and adversarial samples (Thai/English mix, noisy text, missing fields).

### Online (post-deploy)
- Reliability:
  - success rate
  - schema validation pass rate
  - tool error rate
  - p95 latency
  - token cost per ticket
- Decision quality:
  - escalation precision/recall
  - false negatives for critical incidents (highest risk)
  - manual override rate by support leads
- Business impact:
  - time-to-first-response
  - time-to-resolution
  - backlog reduction
  - CSAT trend

### Rollout plan
- Start with shadow mode (AI suggests, humans decide).
- Move to guarded auto-routing for low/medium confidence bands.
- Keep continuous evaluation with weekly error review and prompt/tool updates.
