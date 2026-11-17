# Báo cáo cá nhân — 2A202603802_TranPhamMinhSon

## 1. Thông tin thành viên

- Họ tên: Trần Phạm Minh Sơn
- MSSV: 2A202603802
- Email: sontpmit@gmail.com
- GitHub: sontpm
- Vai trò trong nhóm: Thành viên 5 — Durability & Evaluation Lead
- Nhóm: Vinflow (Lớp L3B)

## 2. Phần việc phụ trách

- **Giai đoạn hiện tại (Checkpoint 3 — Handoff, ledger, crash):**
  - Kiểm tra và xác nhận tính bền vững (`durability`), cơ chế idempotency (`refund:{claim_id}`), truyền `crash_at` và lan truyền ngoại lệ `InjectedCrash` (kèm ghi trace khi crash) trên cả ba shape nhóm viết (`src/lab8/shapes/workflow.py`, `src/lab8/shapes/single.py`, `src/lab8/shapes/orchestrator.py`).
  - Đối chiếu phản ví dụ `lab8.demo.buggy_workflow` để kiểm chứng lý do checkpoint đơn lẻ không thay thế được ledger giao dịch SQLite.
  - Viết test kiểm thử idempotency và crash recovery (tiêu chí C8) tại `src/tests/test_durability_recovery.py`.

## 3. Đóng góp cụ thể

Commit chính: `9f2fb18` (nhánh `sontpm`)

**Kiểm tra và đối chiếu CP3 trên cả 3 shape nhóm viết**

1. **Truyền `crash_at` và không bắt `InjectedCrash`:** Xác nhận cả ba file `src/lab8/shapes/workflow.py`, `src/lab8/shapes/single.py` và `src/lab8/shapes/orchestrator.py` đều gọi `issue_refund(conn, claim_id, proposal, crash_at=crash_at)`. Khi `InjectedCrash` xảy ra, các shape chỉ ghi event `"crash"` vào trace, gọi `trace.write()` để đảm bảo Trace Contract v1, rồi `raise` lại ngoại lệ (không nuốt lỗi).
2. **Idempotency & Ledger giao dịch (`lab8.durability.issue_refund`):**
   - Khóa idempotency là `refund:{claim_id}` trong `refund_ledger`, ghi cùng transaction `BEGIN IMMEDIATE` với audit `refund_committed:{claim_id}` trong `audit_events`.
   - Khi gọi lại cùng claim (`idempotent_replay`) hoặc resume sau điểm crash `after_effect_before_checkpoint`, host phát hiện bản ghi đã commit với cùng số tiền, cập nhật bảng `checkpoints` và không tạo dòng tiền thứ hai.
   - Khi quote mới khác số tiền đã commit (`amount_conflict`), host giữ nguyên số tiền cũ, ghi audit `amount_conflict` và cả 3 shape đều trả `status="failed"`, `error_reason="amount_conflict"`.
   - Khi claim chưa qua cổng policy/approval (ví dụ `C-007` hết hạn approval), `authorize()` từ chối trước điểm ghi/crash và ghi audit `policy_denied`, không tạo dòng ledger.
3. **Phản ví dụ `buggy_workflow`:** Chạy `python -m lab8.demo.buggy_workflow` cho kết quả `unsafe refund rows: 2 (the host ledger must stay at 1)`, minh họa việc chỉ kiểm tra cờ `checkpointed = 1` không bảo vệ được thao tác ghi khi crash xảy ra giữa bước ghi effect và bước cập nhật checkpoint.

**Bài test đã thêm (`src/tests/test_durability_recovery.py` — 21 test cases trong cổng host)**

- `test_idempotent_replay_keeps_single_ledger_row_across_shapes`: chạy lặp lại `C-011` hai lần trên cả 3 shape; xác nhận kết quả `resolved`, `idempotency_key == "refund:C-011"`, đúng 1 dòng `refund_ledger`, 1 audit `refund_committed` và trace hợp lệ.
- `test_crash_and_resume_all_points_across_shapes`: kiểm thử đủ 3 điểm crash (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`) × 3 shape trên `C-012`; kiểm tra trạng thái DB trung gian ngay lúc crash, kiểm tra file crash trace chứa event `"crash"` và không lộ `CANARY_SECRET_*`, và kiểm tra trạng thái sau resume.
- `test_amount_conflict_on_retry_keeps_original_committed_refund`: mô phỏng quote thay đổi trên `C-001` khi gọi lại (`35000` → `20000`); xác nhận cả 3 shape trả `failed` (`amount_conflict`), giữ nguyên dòng ledger `35000` và có audit `amount_conflict`.
- `test_crash_and_resume_preserves_per_order_cap_on_topup`: mô phỏng crash `after_effect_before_checkpoint` rồi resume trên `C-014` (`O-515` đã hoàn `30000`, entitlement `150000`); xác nhận tổng hoàn của đơn giữ ở `150000` (chỉ bù `120000`, không nhân đôi).
- `test_denied_claim_never_writes_ledger_even_with_crash_point`: kiểm tra `C-007` (approval hết hạn) với `crash_at="after_effect_before_checkpoint"` và retry đều bị chặn tại cổng policy với `policy_denied`, không ghi ledger.

## 4. Bằng chứng

Chạy kiểm tra trong `src/` (Python 3.13.5, Windows AMD64):

- `python -m lab8.smoke` → `lab8.smoke pass` (`manifest 1.1 | MockLLM seeded | swarm C-001 refund 35000 | trace clean`).
- `python -m pytest -q tests/test_durability_recovery.py` → `21 passed`.
- `python -m pytest -q` (cổng host) → `126 passed, 248 deselected` (105 test có sẵn + 21 test mới trong `src/tests/test_durability_recovery.py`).
- `python -m pytest -q -m student -o addopts=` → `248 passed, 126 deselected` (toàn bộ ma trận T01–T14 trên 4 shape, gồm T11 và T12).
- `python -m pytest -q -m student -o addopts= -k "test_t11 or test_t12"` → `8 passed, 366 deselected`.
- `python -m lab8.demo.buggy_workflow` → `unsafe refund rows: 2 (the host ledger must stay at 1)`.
- `python -m lab8.crash_test --count 20 --out <temp>` (chạy thử kiểm chứng CP3 trước bước xuất artifact CP4) → `crash_safety 20/20`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (trợ lý AI lập trình).
- **Mục đích sử dụng:**
  - Rà soát code 3 shape (`workflow.py`, `single.py`, `orchestrator.py`) và module host (`durability.py`, `crash_test.py`, `metrics.py`) theo đúng các điều kiện của CP3 trong `CHECKPOINTS.md` và `docs/contracts.md`.
  - Hỗ trợ viết bộ test `src/tests/test_durability_recovery.py`
- **Cách tự kiểm tra:**
  - Tự thiết lập môi trường `.venv` trong `src/` theo `src/requirements.txt`, chạy trực tiếp `lab8.smoke`, `pytest` cổng host, ma trận `student`, `buggy_workflow`, và `crash_test`.
  - Đối chiếu kết quả test và số liệu trong mục 4 trực tiếp từ output lệnh đã chạy; không sửa bất kỳ file thước đo nào của host (`durability.py`, `policy.py`, `metrics.py`, `config/`, `data/`).

## 6. Tự đánh giá

- Hoàn thành đầy đủ phạm vi Checkpoint 3 (CP3) được nhóm trưởng giao: xác minh tính bền vững, idempotency và cơ chế crash/resume trên cả ba shape nhóm viết; bổ sung 21 test case mới vào cổng host (`src/tests/test_durability_recovery.py`) và giữ xanh toàn bộ 126 host tests + 248 student tests.