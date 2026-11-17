"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.

Code / model boundary in this shape:
- Code decides: claim lookup, order ownership, policy, quote amount, approval, write.
- Model (MockLLM) only plans the task wording and drafts the customer reply.
  Its text is never parsed into numbers and never written to the trace.
- The ticket is user data. It is never put in the handoff or the trace.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import ORDER_FIELDS, compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"

# Read-only tools handed to investigators. No write tool is ever listed here;
# make_handoff raises HandoffError if one slips in.
INVESTIGATOR_TOOLS = [
    "lookup_order",
    "lookup_policy",
    "lookup_refund_history",
    "compute_compensation",
]

# Substrings that must never reach a trace file. The grader scans for more
# (phone, address, internal note, item name); those never enter the trace
# because we only record allowlisted order fields.
_FORBIDDEN_MARKERS = ("CANARY_SECRET_", "parent_secret", "raw_headers")


class SafeTrace(Trace):
    """Trace that refuses secret material at write time (defense in depth)."""

    def add(self, kind: str, payload: dict[str, Any]) -> None:
        clean = safe_dump(payload)
        blob = str(clean)
        if any(marker in blob for marker in _FORBIDDEN_MARKERS):
            clean = {"redacted": True, "reason": "secret_marker_blocked"}
        super().add(kind, clean)


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _done(conn, trace, budget, claim_id, seed, status, proposal, reason) -> RunResult:
    trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
    return finish(
        conn,
        shape=SHAPE,
        claim_id=claim_id,
        seed=seed,
        status=status,
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=reason,
    )


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = SafeTrace(make_run_id(SHAPE, claim_id, seed))

    # Step 1 — orchestrator reads the claim through the allowlisted view
    # (claim_id, principal_id, order_id, ticket). No SELECT *, no parent_secret.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        return _done(conn, trace, budget, claim_id, seed, "failed", 0, "unknown_claim")

    trace.add("claim", {"claim_id": claim_id, "has_order_id": bool(claim.get("order_id"))})

    # The model plans from the ticket text. Output is not used for any decision.
    complete(budget, seed=seed, purpose="plan", prompt=claim["ticket"])

    # Missing order_id -> ask for it. Never infer an order id from ticket text.
    if not claim.get("order_id"):
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        return _done(conn, trace, budget, claim_id, seed, "needs_info", 0, "missing_order_id")

    # Step 2 — sanitized handoff. facts is empty on purpose: the investigator
    # reads the order itself through read-only tools, so nothing from the
    # parent context (ticket, secret, headers) crosses the boundary.
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}-s{seed}",
        claim_id=claim_id,
        task="investigate_order_and_policy",
        facts={},
        allowed_tools=list(INVESTIGATOR_TOOLS),
    )
    trace.add("handoff", handoff)

    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    history = tools.get("lookup_refund_history") or {}
    policies = (tools.get("lookup_policy") or {}).get("policies") or []

    trace.add(
        "investigator",
        {
            "order_visible": bool(order_view.get("visible")),
            "order_reason": order_view.get("reason"),
            "order": _order_fields(order_view),
            "current_policy_count": len(policies),
            "refunded_vnd": int(history.get("refunded_vnd") or 0),
            "refund_count": int(history.get("refund_count") or 0),
        },
    )

    # Not found / other principal -> escalate. No phone, address, item, note returned.
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return _done(conn, trace, budget, claim_id, seed, "escalated", 0, order_view.get("reason"))

    # Step 3 — the orchestrator owns the quote. It is computed by code from the
    # structured order row, never from ticket text or model output.
    order = _order_fields(order_view)
    quote_payload = tools.get("compute_compensation")
    if not quote_payload:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
    proposal = int(quote_payload["amount_vnd"])
    trace.add(
        "quote",
        {
            "amount_vnd": proposal,
            "reason": quote_payload.get("reason"),
            "clause_ids": list(quote_payload.get("clause_ids") or []),
            "parts": dict(quote_payload.get("parts") or {}),
        },
    )

    if proposal <= 0:
        complete(budget, seed=seed, purpose="draft", prompt="denied")
        return _done(conn, trace, budget, claim_id, seed, "denied", 0, quote_payload.get("reason"))

    # Step 4 — host gate. Full quote in; host checks approval, per-order cap,
    # idempotency. crash_at is forwarded and InjectedCrash is not swallowed.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    effect = outcome.get("effect") or {}
    trace.add(
        "host",
        {
            "ok": bool(outcome["ok"]),
            "reason": outcome["reason"],
            "conflict": bool(outcome["conflict"]),
            "committed_vnd": int(effect.get("amount_vnd") or 0),
        },
    )
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return _done(conn, trace, budget, claim_id, seed, status, proposal, outcome["reason"])
    return _done(conn, trace, budget, claim_id, seed, "resolved", proposal, None)


def _order_fields(order_view: dict[str, Any]) -> dict[str, Any]:
    """Re-apply the order allowlist so only non-PII fields can be traced or quoted."""
    order = order_view.get("order") or {}
    return {key: order[key] for key in ORDER_FIELDS if key in order}
