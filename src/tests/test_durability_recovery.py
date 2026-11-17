"""
CP3 durability, idempotency, and crash-recovery tests across all student shapes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import check_trace
from lab8.policy import order_refunded_vnd
from lab8.shapes import SHAPES
from lab8.schemas import make_run_id

STUDENT_SHAPES = ("workflow", "single", "orchestrator")
CRASH_POINTS = ("before_effect", "after_effect_before_checkpoint", "after_checkpoint")


@pytest.fixture
def run_in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate Trace output directory so tests do not dirty `src/traces/`."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_idempotent_replay_keeps_single_ledger_row_across_shapes(public_db, run_in_tmp: Path, shape: str):
    run_claim = SHAPES[shape]
    first = run_claim("C-011", seed=11, store_path=str(public_db))
    started_second = time.time()
    second = run_claim("C-011", seed=11, store_path=str(public_db))

    assert first.status == "resolved"
    assert second.status == "resolved"
    assert second.proposal_amount == 35000
    assert len(second.refund_effects) == 1
    assert int(second.refund_effects[0]["amount_vnd"]) == 35000
    assert second.refund_effects[0]["idempotency_key"] == "refund:C-011"
    assert second.committed_audit_count == 1

    trace_ok, trace_reason = check_trace(second.as_dict(), started_at=started_second)
    assert trace_ok, trace_reason

    conn = connect(public_db)
    try:
        ledger_count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
        assert ledger_count == 1
        assert committed_audit_count(conn, "C-011") == 1
    finally:
        conn.close()


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_crash_and_resume_all_points_across_shapes(
    public_db,
    run_in_tmp: Path,
    shape: str,
    crash_point: str,
):
    run_claim = SHAPES[shape]
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(public_db), crash_at=crash_point)

    # Crash trace must be flushed with matching run_id and without secret leakage.
    run_id = make_run_id(shape, "C-012", 11)
    crash_trace_path = run_in_tmp / "traces" / f"{run_id}.json"
    assert crash_trace_path.is_file(), f"missing crash trace for {shape} at {crash_point}"
    crash_trace_text = crash_trace_path.read_text(encoding="utf-8")
    crash_trace = json.loads(crash_trace_text)
    assert crash_trace["run_id"] == run_id
    assert any(ev.get("kind") == "crash" for ev in crash_trace["events"])
    assert "CANARY_SECRET_" not in crash_trace_text

    conn = connect(public_db)
    try:
        mid_effect = get_refund(conn, "C-012")
        mid_audits = committed_audit_count(conn, "C-012")
        mid_checkpoint = conn.execute(
            "SELECT 1 FROM checkpoints WHERE claim_id = 'C-012' AND step = 'issue_refund'"
        ).fetchone()
    finally:
        conn.close()

    if crash_point == "before_effect":
        assert mid_effect is None
        assert mid_audits == 0
        assert mid_checkpoint is None
    elif crash_point == "after_effect_before_checkpoint":
        assert mid_effect is not None and int(mid_effect["amount_vnd"]) == 35000
        assert mid_audits == 1
        assert mid_checkpoint is None
    else:
        assert mid_effect is not None and int(mid_effect["amount_vnd"]) == 35000
        assert mid_audits == 1
        assert mid_checkpoint is not None

    started_resume = time.time()
    resumed = run_claim("C-012", seed=11, store_path=str(public_db), crash_at=None)
    assert resumed.status == "resolved"
    assert resumed.proposal_amount == 35000
    assert len(resumed.refund_effects) == 1
    assert int(resumed.refund_effects[0]["amount_vnd"]) == 35000
    assert resumed.committed_audit_count == 1

    trace_ok, trace_reason = check_trace(resumed.as_dict(), started_at=started_resume)
    assert trace_ok, trace_reason

    conn = connect(public_db)
    try:
        ledger_count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
        checkpoint = conn.execute(
            "SELECT 1 FROM checkpoints WHERE claim_id = 'C-012' AND step = 'issue_refund'"
        ).fetchone()
        assert ledger_count == 1
        assert committed_audit_count(conn, "C-012") == 1
        assert checkpoint is not None
    finally:
        conn.close()


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_amount_conflict_on_retry_keeps_original_committed_refund(public_db, run_in_tmp: Path, shape: str):
    run_claim = SHAPES[shape]
    first = run_claim("C-001", seed=11, store_path=str(public_db))
    assert first.status == "resolved"
    assert int(first.refund_effects[0]["amount_vnd"]) == 35000

    # Simulate a changed quote on retry (shipping_fee_vnd reduced from 35000 to 20000).
    conn = connect(public_db)
    try:
        conn.execute("UPDATE orders SET shipping_fee_vnd = 20000 WHERE order_id = 'O-107'")
        conn.commit()
    finally:
        conn.close()

    retry = run_claim("C-001", seed=11, store_path=str(public_db))
    assert retry.status == "failed"
    assert retry.error_reason == "amount_conflict"
    assert retry.proposal_amount == 20000
    assert len(retry.refund_effects) == 1
    assert int(retry.refund_effects[0]["amount_vnd"]) == 35000
    assert retry.committed_audit_count == 1

    conn = connect(public_db)
    try:
        effect = get_refund(conn, "C-001")
        assert effect is not None and int(effect["amount_vnd"]) == 35000
        conflict_audit = conn.execute(
            "SELECT details_json FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'amount_conflict'"
        ).fetchone()
        assert conflict_audit is not None
        details = json.loads(conflict_audit["details_json"])
        assert details == {"committed_vnd": 35000, "attempted_vnd": 20000}
    finally:
        conn.close()


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_crash_and_resume_preserves_per_order_cap_on_topup(public_db, run_in_tmp: Path, shape: str):
    """C-014 on O-515 (prior refund 30k, damage quote 150k -> net 120k) survives crash without double-paying."""
    run_claim = SHAPES[shape]
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-014",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

    resumed = run_claim("C-014", seed=11, store_path=str(public_db), crash_at=None)
    assert resumed.status == "resolved"
    assert resumed.proposal_amount == 150000
    assert len(resumed.refund_effects) == 1
    assert int(resumed.refund_effects[0]["amount_vnd"]) == 120000
    assert resumed.committed_audit_count == 1

    conn = connect(public_db)
    try:
        assert order_refunded_vnd(conn, "O-515") == 150000
        assert committed_audit_count(conn, "C-014") == 1
    finally:
        conn.close()


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_denied_claim_never_writes_ledger_even_with_crash_point(public_db, run_in_tmp: Path, shape: str):
    """Expired approval (C-007) fails at host policy gate before crash/commit and never writes ledger."""
    run_claim = SHAPES[shape]
    first = run_claim(
        "C-007",
        seed=11,
        store_path=str(public_db),
        crash_at="after_effect_before_checkpoint",
    )
    second = run_claim("C-007", seed=11, store_path=str(public_db))

    for res in (first, second):
        assert res.status == "denied"
        assert res.proposal_amount == 35000
        assert res.refund_effects == []
        assert res.committed_audit_count == 0

    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-007") is None
        assert committed_audit_count(conn, "C-007") == 0
        denied = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-007' AND event_type = 'policy_denied'"
        ).fetchone()["n"]
        assert denied >= 1
    finally:
        conn.close()
