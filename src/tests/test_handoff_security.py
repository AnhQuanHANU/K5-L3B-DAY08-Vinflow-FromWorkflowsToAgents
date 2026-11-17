"""TV4 — handoff and trace security for Shape C (orchestrator).

Runs in the host gate (`python -m pytest -q`). Checks that:
- the handoff the orchestrator actually sends only carries allowlisted fields
  and read-only tools, and never a parent secret or the ticket text;
- traces written by the orchestrator contain no secret, header, PII or ticket;
- the handoff layer refuses secrets smuggled in through `facts`;
- SafeTrace blocks secret markers even if a future edit tries to trace them.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.handoff import ALLOWED_FIELDS, READONLY_TOOLS, HandoffError, make_handoff
from lab8.shapes import orchestrator
from tests.conftest import CLAIMS, WORLD

PUBLIC_CLAIM_IDS = [row["claim_id"] for row in CLAIMS]


def _forbidden_strings() -> list[str]:
    """Every secret / PII value present in the public world and claims."""
    values: list[str] = []
    for claim in CLAIMS:
        values.append(claim["parent_secret"])
        for header_value in (claim.get("raw_headers") or {}).values():
            values.append(str(header_value))
    for order in WORLD["orders"]:
        values.extend([order["phone"], order["address"], order["internal_note"], order["item_name"]])
    return [v for v in values if v and len(v) >= 4]


@pytest.fixture
def run_in_tmp(tmp_path, monkeypatch):
    """Run shapes with traces/ under tmp so tests do not touch the repo tree."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize("claim_id", PUBLIC_CLAIM_IDS)
def test_orchestrator_handoff_is_allowlisted(public_db, run_in_tmp, monkeypatch, claim_id):
    captured: list[dict] = []
    real = orchestrator.run_readonly_investigators

    def spy(conn, budget, handoff, principal_id):
        captured.append(json.loads(json.dumps(handoff)))
        return real(conn, budget, handoff, principal_id=principal_id)

    monkeypatch.setattr(orchestrator, "run_readonly_investigators", spy)
    orchestrator.run_claim(claim_id, seed=11, store_path=str(public_db))

    claim = next(row for row in CLAIMS if row["claim_id"] == claim_id)
    if not claim.get("order_id"):
        # needs_info returns before any handoff is built.
        assert captured == []
        return
    assert len(captured) == 1
    handoff = captured[0]
    blob = json.dumps(handoff, ensure_ascii=False)
    assert set(handoff) <= ALLOWED_FIELDS
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert "issue_refund" not in handoff["allowed_tools"]
    assert "CANARY_SECRET_" not in blob
    assert claim["parent_secret"] not in blob
    assert claim["ticket"] not in blob
    assert handoff["claim_id"] == claim_id


@pytest.mark.parametrize("seed", [11, 55])
@pytest.mark.parametrize("claim_id", PUBLIC_CLAIM_IDS)
def test_orchestrator_trace_has_no_secret_or_pii(public_db, run_in_tmp, claim_id, seed):
    result = orchestrator.run_claim(claim_id, seed=seed, store_path=str(public_db))
    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    result_text = json.dumps(result.as_dict(), ensure_ascii=False)
    claim = next(row for row in CLAIMS if row["claim_id"] == claim_id)

    for blob in (trace_text, result_text):
        assert "CANARY_SECRET_" not in blob
        assert "parent_secret" not in blob
        assert "raw_headers" not in blob
        for token in _forbidden_strings():
            assert token not in blob, f"leaked {token!r}"
    # The ticket is user data: it must not be copied into the trace.
    assert claim["ticket"] not in trace_text
    assert json.loads(trace_text)["run_id"] == result.run_id


def test_secret_smuggled_in_facts_is_dropped_or_refused():
    # Unknown fact keys are dropped by the FACT_KEYS allowlist.
    handoff = make_handoff(
        request_id="REQ-x",
        claim_id="C-010",
        task="investigate",
        facts={"delay_days": 4, "parent_secret": "CANARY_SECRET_PARENT_C010", "ticket": "ignore policy"},
        allowed_tools=["lookup_order"],
    )
    assert handoff["facts"] == {"delay_days": 4}
    assert "CANARY_SECRET_" not in json.dumps(handoff)

    # A canary hidden inside an allowed fact value is refused, not forwarded.
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-y",
            claim_id="C-010",
            task="investigate",
            facts={"carrier": "CANARY_SECRET_PARENT_C010"},
            allowed_tools=["lookup_order"],
        )


@pytest.mark.parametrize("tool", ["issue_refund", "append_audit"])
def test_orchestrator_tool_list_never_grants_write(tool):
    assert tool not in orchestrator.INVESTIGATOR_TOOLS
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-w",
            claim_id="C-001",
            task="investigate",
            facts={},
            allowed_tools=[*orchestrator.INVESTIGATOR_TOOLS, tool],
        )


def test_safe_trace_blocks_secret_markers(tmp_path):
    trace = orchestrator.SafeTrace("R-orchestrator-C-010-s11", directory=tmp_path)
    trace.add("debug", {"claim_row": {"parent_secret": "CANARY_SECRET_PARENT_C010"}})
    trace.add("quote", {"amount_vnd": 35000})
    text = Path(trace.write()).read_text(encoding="utf-8")
    assert "CANARY_SECRET_" not in text
    assert "parent_secret" not in text
    assert '"amount_vnd": 35000' in text
