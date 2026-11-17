# Báo cáo cá nhân — 2A202603797_NguyenDinhNam

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Nam
- MSSV: 2A202603797
- Email: dinhnam260904@gmail.com
- GitHub: dinhnam269

## 2. Phần việc phụ trách

- **Vai trò:** Workflow Engineer
- **Module phụ trách:** Toàn bộ **Shape A (`workflow`)** tại `src/lab8/shapes/workflow.py` (bao gồm phần luồng xử lý CP2 và xử lý crash CP3).
- **Test phụ trách (C8):** Bổ sung test case kiểm tra biên cho `workflow` tại `src/tests/test_workflow_edge.py` (`test_workflow_delay_exactly_3_days_resolves`, `test_workflow_zero_shipping_fee_denies_without_ledger`).

## 3. Đóng góp cụ thể

- **Commit chính (trên nhánh `dev-DinhNam`):**
  - `ddb6549` — `feat(workflow): implement Shape A workflow (CP2)`: cài đặt luồng xử lý claim cố định cho Shape A.
  - Bổ sung phần CP3 tại `src/lab8/shapes/workflow.py` (truyền `crash_at` vào `durability.issue_refund`, ghi trace và re-raise `InjectedCrash`).
- **Quyết định kỹ thuật:**
  - Đọc dữ liệu qua `get_claim_view` và `lookup_order` (không dùng `SELECT *`), không ghi PII hay `CANARY_SECRET_*` vào trace.
  - Luôn tính tiền bằng `compute_compensation(conn, order)` từ dữ liệu DB, bỏ qua con số trễ viết trong ticket để tránh prompt injection và giữ `variance = 0`.
  - Khi `proposal > 0`, truyền **quote đầy đủ** vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` để Host tự kiểm duyệt approval, trừ phần đã hoàn của các claim trước (T13, T14) và ghi audit `policy_denied` khi cần.
  - Chuẩn hóa mọi nhánh kết quả (`resolved`, `needs_info`, `escalated`, `denied`, `failed`) qua `lab8.shapes.common.finish()`.

## 4. Bằng chứng

- **Nhánh & Commit:** Nhánh `dev-DinhNam`, commit `ddb6549` (CP2) và commit tiếp theo cho CP3 + test biên + báo cáo cá nhân.
- **Test đã thêm:** `src/tests/test_workflow_edge.py` (`test_workflow_delay_exactly_3_days_resolves`, `test_workflow_zero_shipping_fee_denies_without_ledger`).
- **Kết quả kiểm thử đã chạy trong `src/`:**
  - `python -m pytest -q`: **56 passed** (cổng host + 2 test biên xanh).
  - `python -m pytest -q -m student -o addopts= -k workflow`: **62 passed** (bao gồm cả T11 idempotency và T12 crash & resume).

## 5. Công cụ AI đã dùng

- Sử dụng trợ lý AI trong IDE để hỗ trợ tóm tắt yêu cầu lab, triển khai `src/lab8/shapes/workflow.py`, thao tác Git sửa commit message và soạn thảo báo cáo cá nhân.
- **Cách tự kiểm tra:** Đối chiếu từng nhánh xử lý với `docs/business_rules.md` và `docs/contracts.md`; chạy trực tiếp `pytest` cho cổng host (54/54 pass) và toàn bộ bộ test student của `workflow` (62/62 pass).

## 6. Tự đánh giá

- Đã hoàn thành phần cài đặt Shape A (`workflow`) cho CP2 và CP3, bổ sung 2 test case biên tại `src/tests/test_workflow_edge.py`, đảm bảo an toàn trace/PII và idempotency khi crash.
- Việc cần làm tiếp ở bước tổng hợp nhóm: điền dòng đóng góp vào `TEAM.md` và cùng nhóm chạy `check_submission` trước khi nộp.
