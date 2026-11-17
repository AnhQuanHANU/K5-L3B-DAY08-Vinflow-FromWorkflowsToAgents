"""Integration and Environment Verification Tests for Team Vinflow (Role 1: Nguyễn Anh Quân - 2A202603892).
Part of Checkpoint 1 (CP1) deliverable.
"""

import pytest
from lab8.schemas import RunResult, STATUSES
from lab8.db import connect

def test_integration_environment_and_db_tables(public_db):
    """Xác thực cơ sở dữ liệu giả lập LogiX-VN được khởi tạo đầy đủ các bảng cần thiết."""
    conn = connect(public_db)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    expected_tables = {"claims", "orders", "policies", "refund_ledger", "audit_events"}
    assert expected_tables.issubset(tables), f"Thiếu các bảng cơ sở dữ liệu: {expected_tables - tables}"

def test_integration_run_result_schema_contract():
    """Kiểm tra tính hợp lệ của RunResult schema theo contract của hệ thống."""
    res = RunResult(
        run_id="workflow-C-001-11",
        claim_id="C-001",
        shape="workflow",
        seed=11,
        status="resolved",
        proposal_amount=35000,
        refund_effects=[{"claim_id": "C-001", "amount": 35000}],
        committed_audit_count=1,
        model_calls=0,
        tool_calls=2,
        input_tokens=0,
        output_tokens=0,
        cost_estimate=0.0,
        trace_path="dummy_trace.json",
        error_reason=None,
    )
    res_dict = res.as_dict()
    assert res_dict["status"] in STATUSES
    assert res_dict["proposal_amount"] == 35000
    assert len(res_dict["refund_effects"]) == 1
    assert res_dict["committed_audit_count"] == 1
