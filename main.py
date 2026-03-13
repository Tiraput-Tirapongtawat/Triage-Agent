from __future__ import annotations

import argparse

from fixtures import load_sample_tickets
from format import SupportTicket, TriageResult
from triage_engine import triage_ticket
from ai_agent import triage_ticket_with_ai


def _select_tickets(
    tickets: list[SupportTicket], ticket_id: str | None
) -> list[SupportTicket]:
    if not ticket_id:
        return tickets
    selected = [ticket for ticket in tickets if ticket.ticket_id == ticket_id]
    if not selected:
        raise ValueError(f"Ticket id not found: {ticket_id}")
    return selected


def _compare_expected(ticket: SupportTicket, result: TriageResult) -> tuple[bool, str]:
    if ticket.expected is None:
        return True, "skipped (no expected outcome provided)"

    urgency_ok = result.urgency == ticket.expected.urgency
    action_ok = result.next_action == ticket.expected.next_action
    route_ok = result.route_team == ticket.expected.route_team
    all_ok = urgency_ok and action_ok and route_ok
    detail = f"urgency={urgency_ok}, next_action={action_ok}, route_team={route_ok}"
    return all_ok, detail


def run(mode: str, ticket_id: str | None) -> int:
    tickets = _select_tickets(load_sample_tickets(), ticket_id)
    passed = 0
    with_expected = 0

    if mode == "ai":
        triage_fn = triage_ticket_with_ai
        print("Mode: ai (OpenAI + tool-calling agent)")
    else:
        triage_fn = triage_ticket
        print("Mode: mock (deterministic rules)")

    print(f"Loaded {len(tickets)} ticket(s).\n")

    for ticket in tickets:
        try:
            result = triage_fn(ticket)
        except Exception as exc:
            print(f"Ticket: {ticket.ticket_id}")
            print(f"Error: {exc}")
            return 1

        ok, check_detail = _compare_expected(ticket, result)

        print(f"Ticket: {ticket.ticket_id}")
        print(f"Checks: {check_detail}")
        print(result.model_dump_json(indent=2))
        print("-" * 72)

        if ticket.expected is not None:
            with_expected += 1
            passed += int(ok)

    if with_expected == 0:
        print("Summary: no expected outcomes were provided; smoke run completed.")
        return 0

    print(f"Summary: {passed}/{with_expected} tickets matched expected outcomes.")
    return 0 if passed == with_expected else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Support Ticket Triage Agent Runner")
    parser.add_argument(
        "--mode",
        choices=["mock", "ai"],
        default="mock",
        help="mock: deterministic rules, ai: OpenAI tool-calling agent",
    )
    parser.add_argument(
        "--ticket-id",
        default=None,
        help="Run a single ticket by id (e.g., ticket_001_billing_duplicate_charge)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(run(mode=args.mode, ticket_id=args.ticket_id))
