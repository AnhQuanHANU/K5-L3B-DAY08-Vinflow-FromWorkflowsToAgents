# Báo cáo cá nhân — 2A202603810_PhanTranManhCuong

## 1. Thông tin thành viên

- Họ tên: Phan Trần Mạnh Cường
- MSSV: 2A202603810
- Email: manhcuong2005.28@gmail.com
- GitHub: Cuongngucute
- Vai trò trong nhóm: Thành viên 4 — Orchestrator & Security Lead

## 2. Phần việc phụ trách

- Shape C `orchestrator` tại `src/lab8/shapes/orchestrator.py` (CP2, CP3).
- Ranh giới bảo mật của shape C: handoff theo allowlist (`handoff.v1`) và trace đúng Trace contract v1, không lộ `CANARY_SECRET_*` hay PII (CP3, CP4).
- Test bảo mật handoff/trace: `src/tests/test_handoff_security.py`.

## 3. Đóng góp cụ thể

Commit chính: `<điền hash sau khi commit>`

**Luồng shape C**

1. Orchestrator đọc claim bằng `get_claim_view` (chỉ `claim_id`, `principal_id`, `order_id`, `ticket`), không `SELECT *`, nên `parent_secret` và `raw_headers_json` không bao giờ được nạp vào shape.
2. Claim không tồn tại → `failed`. Thiếu `order_id` → `needs_info`, không đoán mã đơn từ chữ trong ticket.
3. Dựng handoff bằng `make_handoff` với `facts={}` và 4 tool chỉ đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`. Investigator tự đọc order qua tool, nên không có dữ kiện nào của parent context (ticket, secret, header) đi qua ranh giới.
4. `run_readonly_investigators` chạy các tool trên. Đơn không thấy / không thuộc principal → `escalated`, không trả SĐT, địa chỉ, tên hàng, ghi chú nội bộ.
5. Tiền do code tính (`compute_compensation` trên dòng order có cấu trúc), không do MockLLM. Quote = 0 → `denied`, không gọi host.
6. Quote > 0 → gọi `durability.issue_refund(conn, claim_id, quote, crash_at=crash_at)` với **quote đầy đủ**. Host tự trừ phần đơn đã được hoàn (T13, T14), kiểm approval và idempotency. `InjectedCrash` không bị bắt: ghi trace rồi ném lại (T12).
7. Trả kết quả qua `lab8.shapes.common.finish()` ở mọi nhánh, nên trace luôn được ghi kể cả khi return sớm.

**Quyết định kỹ thuật**

- **Ranh giới code / model:** MockLLM chỉ lập kế hoạch (`plan`) và soạn câu trả lời (`draft`). Chữ model sinh ra không được parse thành số, không dùng cho quyết định nào và không ghi vào trace.
- **Vì sao truyền quote đầy đủ:** host đọc lại tổng đã hoàn của đơn trong cùng transaction ghi. Nếu shape tự trừ trước thì bị trừ hai lần (T14 sẽ ra 90.000 thay vì 120.000).
- **`SafeTrace`:** lớp con của `lab8.trace.Trace`. Payload nào chứa `CANARY_SECRET_`, `parent_secret` hoặc `raw_headers` bị thay bằng `{"redacted": true}` trước khi ghi. Đây là lớp phòng thủ thêm; lớp chính vẫn là chỉ ghi field allowlist.
- **Field cố ý không ghi vào trace:** ticket (dữ liệu người dùng, có thể chứa injection hoặc PII), `principal_id`, `parent_secret`, header, SĐT, địa chỉ, `internal_note`, `item_name`, output của model. Order chỉ ghi các field trong `ORDER_FIELDS`.
- **Event trong trace:** `claim` (chỉ có cờ `has_order_id`), `handoff` (đã sanitize), `investigator` (order allowlist, số policy hiện hành, tổng đã hoàn), `quote`, `host` (kết quả cổng duyệt), `crash` (nếu có), `decision`.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k orchestrator` → `62 passed` (T01–T14 trên 5 seed, gồm T11 retry và T12 crash rồi resume).
- `python -m pytest -q` (cổng host) → `100 passed` (54 test có sẵn + 46 test mới trong `test_handoff_security.py`).
- `python -m lab8.crash_test --count 20` → `crash_safety 20/20`.
- Test đã thêm trong `src/tests/test_handoff_security.py`:
  - `test_orchestrator_handoff_is_allowlisted`: bắt handoff orchestrator thật sự gửi đi trên cả 14 claim public; kiểm chỉ có field allowlist, chỉ tool đọc, không có secret hay ticket.
  - `test_orchestrator_trace_has_no_secret_or_pii`: quét trace và `RunResult` ở seed 11 và 55, tìm mọi secret, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng có trong world.
  - `test_secret_smuggled_in_facts_is_dropped_or_refused`: key lạ trong `facts` bị loại; canary nằm trong giá trị field hợp lệ thì bị từ chối (`HandoffError`).
  - `test_orchestrator_tool_list_never_grants_write`: `issue_refund`, `append_audit` không cấp được cho investigator.
  - `test_safe_trace_blocks_secret_markers`: `SafeTrace` chặn payload chứa marker secret.

## 5. Công cụ AI đã dùng

- **Claude Code:** đọc tài liệu và code host của repo, viết `orchestrator.py` và `test_handoff_security.py`.
- **Cách tự kiểm tra:**
  - Chạy lại ma trận student của orchestrator (62 passed), cổng host (100 passed) và crash suite (20/20) trên máy mình, Python 3.13.
  - Đối chiếu từng nhánh return với bảng output contract trong `docs/contracts.md` và luật trong `docs/business_rules.md`.
  - Đọc trace sinh ra trong `src/traces/` để xác nhận không có ticket hay PII.
- Không dùng AI để bịa số liệu: mọi con số ở mục 4 lấy từ output lệnh chạy thật.

## 6. Tự đánh giá

- Hoàn thành phần shape C và phần bảo mật handoff/trace được giao; shape qua đủ 62 test public và không ảnh hưởng cổng host.
- Giới hạn:
  - Kiểm tra lộ thông tin mới dựa trên dữ liệu public và MockLLM; chưa chạy trên bộ hidden `student_drop/`.
  - `SafeTrace` chỉ chặn theo marker đã biết; lớp bảo vệ chính vẫn là allowlist.
