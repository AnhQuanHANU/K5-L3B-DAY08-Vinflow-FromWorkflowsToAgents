"""Edge-case tests for Shape A (workflow)."""

from __future__ import annotations

from lab8.db import connect
from lab8.shapes.workflow import run_claim


def _seed_case(
    store_path,
    *,
    claim_id: str,
    order_id: str,
    delay_days: int,
    shipping_fee_vnd: int,
    approval_id: str | None = None,
    approved_vnd: int = 0,
) -> None:
    conn = connect(store_path)
    try:
        conn.execute(
            """
            INSERT INTO orders (
                order_id, principal_id, status, delay_days, shipping_fee_vnd,
                paid_vnd, damage_verified, carrier, phone, address, internal_note, item_name
            )
            VALUES (?, 'P-100', 'delivered_late', ?, ?, 150000, 0, 'LOGIX_LOCAL',
                    '0901000999', '123 Nguyen Hue', 'CANARY_INTERNAL_EDGE', 'Test item')
            """,
            (order_id, delay_days, shipping_fee_vnd),
        )
        conn.execute(
            """
            INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
            VALUES (?, 'P-100', ?, 'edge case test', 'CANARY_SECRET_PARENT_EDGE', '{}', ?)
            """,
            (claim_id, order_id, approval_id),
        )
        if approval_id is not None:
            conn.execute(
                """
                INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at)
                VALUES (?, ?, ?, 'valid', '2027-12-31')
                """,
                (approval_id, claim_id, approved_vnd),
            )
        conn.commit()
    finally:
        conn.close()


def test_workflow_delay_exactly_3_days_resolves(public_db):
    _seed_case(
        public_db,
        claim_id="C-EDGE-3D",
        order_id="O-EDGE-3D",
        delay_days=3,
        shipping_fee_vnd=25000,
        approval_id="APP-EDGE-3D",
        approved_vnd=25000,
    )
    result = run_claim("C-EDGE-3D", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 25000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 25000
    assert result.committed_audit_count == 1


def test_workflow_zero_shipping_fee_denies_without_ledger(public_db):
    _seed_case(
        public_db,
        claim_id="C-EDGE-ZERO",
        order_id="O-EDGE-ZERO",
        delay_days=5,
        shipping_fee_vnd=0,
    )
    result = run_claim("C-EDGE-ZERO", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
