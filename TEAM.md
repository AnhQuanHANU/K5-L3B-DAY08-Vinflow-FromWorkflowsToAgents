# Team

## Thông tin nhóm

- Tên nhóm: Vinflow
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Vinflow-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: https://github.com/AnhQuanHANU/K5-Day8-Vinflow-From-Workflows-to-Agents, main

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | --- | --- | --- | --- | --- |
| 1 | Nguyễn Anh Quân | 2A202603892 | quan.na2A202603892@vinuni.edu.vn | AnhQuanHANU | Integration & Coordination Lead (Role 1) |
| 2 | Nguyễn Đình Nam | 2A202603797 | dinhnam260904@gmail.com | dinhnam269 | Workflow Engineer (Role 2) |
| 3 | Hồ Anh Tú | 2A202603811 | 26ai.tuha2@vinuni.edu.vn | TuHoAnh | Single Agent Engineer (Role 3) |
| 4 | Phan Trần Mạnh Cường | 2A202603810 | manhcuong2005.28@gmail.com | Cuongngucute | Orchestrator & Security Lead (Role 4) |
| 5 | Trần Phạm Minh Sơn | 2A202603802 | sontpmit@gmail.com | sontpm | Durability & Evaluation Lead (Role 5) |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Anh Quân | Integration & Coordination Lead | 27def93 | `src/tests/test_integration_smoke.py` |
| Nguyễn Đình Nam | Workflow Engineer | 4481fbf | `src/tests/test_workflow_edge.py` |
| Hồ Anh Tú | Single Agent Engineer | 7488543 | `src/tests/test_single_prompt_safety.py` |
| Phan Trần Mạnh Cường | Orchestrator & Security Lead | 0009e06 | `src/tests/test_handoff_security.py` |
| Trần Phạm Minh Sơn | Durability & Evaluation Lead | 9f2fb18 | `src/tests/test_durability_recovery.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603892_NguyenAnhQuan

### Phần việc phụ trách

- Quản lý repository GitHub nhóm, cấu hình môi trường runner trên Windows / Python 3.13+.
- Điều phối tiến độ cả nhóm qua 5 checkpoints CP1–CP5 của Lab 8.
- Khởi tạo tài liệu nhóm `TEAM.md`, ma trận phân công 5 thành viên và cấu trúc báo cáo.
- Cài đặt bài test tích hợp môi trường `src/tests/test_integration_smoke.py`.
- Tổng hợp báo cáo nhóm `report/team/group_report.md` và kiểm tra nộp bài `check_submission`.

### Đóng góp cụ thể

- Hoàn thành thiết lập CP1: xác thực smoke test và 54 host tests xanh 100%.
- Cấu hình phân công vai trò nhóm Vinflow cho 5 thành viên, thiết lập chiến lược phân nhánh chống xung đột merge.
- Viết test suite tích hợp đảm bảo môi trường runner đồng nhất và database sẵn sàng.
- Tích hợp các nhánh từ các thành viên vào `main`, chạy bộ kiểm tra nộp bài `check_submission`.

### Bằng chứng

- Commit: `27def93`, `08a41d4`.
- File báo cáo cá nhân: `report/team/2A202603892_NguyenAnhQuan.md`.
- Test suite: `src/tests/test_integration_smoke.py`.

## 2A202603797_NguyenDinhNam

### Phần việc phụ trách

- Cài đặt toàn bộ Shape A (`workflow`) tại `src/lab8/shapes/workflow.py` (CP2, CP3).
- Bổ sung test case kiểm tra biên cho workflow tại `src/tests/test_workflow_edge.py`.
- Hoàn thiện báo cáo cá nhân `report/team/2A202603797_NguyenDinhNam.md`.

### Đóng góp cụ thể

- Xây dựng luồng xử lý cố định cho Shape A, đọc view bảo vệ `get_claim_view` và `lookup_order`, không dùng `SELECT *`.
- Tính toán tiền bồi thường bằng `compute_compensation(conn, order)` trực tiếp từ dữ liệu DB, bỏ qua văn bản ticket để chống prompt injection và triệt tiêu variance.
- Truyền quote đầy đủ và `crash_at` vào `durability.issue_refund`, bắt `InjectedCrash` ghi trace và re-raise đúng hợp đồng CP3.
- Chuẩn hóa mọi nhánh kết quả qua `lab8.shapes.common.finish()`.
- Thêm 2 test biên: `test_workflow_delay_exactly_3_days_resolves` và `test_workflow_zero_shipping_fee_denies_without_ledger`.

### Bằng chứng

- Commit: `4481fbf` (nhánh `dev-DinhNam`).
- File báo cáo cá nhân: `report/team/2A202603797_NguyenDinhNam.md`.
- Test suite: `src/tests/test_workflow_edge.py`, 62/62 student tests cho Shape A passed.

## 2A202603811_HoAnhTu

### Phần việc phụ trách

- Cài đặt toàn bộ Shape B (Single ReAct Agent) tại `src/lab8/shapes/single.py` (CP2, CP3).
- Xây dựng test suite kiểm tra an toàn chống prompt injection và cách ly quyền ghi tool tại `src/tests/test_single_prompt_safety.py`.
- Hoàn thiện báo cáo cá nhân `report/team/2A202603811_HoAnhTu.md`.

### Đóng góp cụ thể

- Cài đặt vòng lặp ReAct bằng `lab8.runtime.run_react` (`max_steps=8`, `worker=True`), chỉ cấp read-only tools và chặn hoàn toàn `issue_refund` trong vòng lặp.
- Đảm bảo agent đọc sự thật từ dòng order qua `lookup_order`, không tin số ngày trễ hay câu lệnh giả mạo trong `ticket`, truyền quote đầy đủ và `crash_at` vào `durability.issue_refund`.
- Ghi trace đúng Trace contract v1, không lưu secret hay `ticket` thô.
- Bổ sung 3 test case kiểm tra chống prompt injection và `ToolRejected` khi gọi write tool.

### Bằng chứng

- Commit: `7488543` (nhánh `hoanhtu-TV3`).
- File báo cáo cá nhân: `report/team/2A202603811_HoAnhTu.md`.
- Test suite: `src/tests/test_single_prompt_safety.py` (3/3 passed), 62/62 student tests của Shape B passed.

## 2A202603810_PhanTranManhCuong

### Phần việc phụ trách

- Cài đặt Shape C `orchestrator` tại `src/lab8/shapes/orchestrator.py` (CP2, CP3).
- Ranh giới bảo mật của shape C: handoff theo allowlist (`handoff.v1`) và trace đúng Trace contract v1, không lộ `CANARY_SECRET_*` hay PII (CP3, CP4).
- Test bảo mật handoff/trace: `src/tests/test_handoff_security.py`.
- Hoàn thiện báo cáo cá nhân `report/team/2A202603810_PhanTranManhCuong.md`.

### Đóng góp cụ thể

- Xây dựng luồng Orchestrator đọc claim qua view bảo vệ, khởi tạo handoff chỉ chứa allowlist field và 4 read-only tools.
- Tách biệt rõ ràng ranh giới code/model: MockLLM chỉ đóng vai trò lập kế hoạch (`plan`) và soạn thảo (`draft`), toàn bộ quyết định tài chính do code kiểm soát.
- Thiết kế lớp phòng thủ `SafeTrace` kế thừa từ `lab8.trace.Trace` để tự động redact các chuỗi canary secret marker.
- Bổ sung 5 test case kiểm thử chuyên sâu bảo mật handoff và trace (`test_orchestrator_handoff_is_allowlisted`, `test_orchestrator_trace_has_no_secret_or_pii`, v.v.).

### Bằng chứng

- Commit: `0009e06` (nhánh `feature/tv4-orchestrator`).
- File báo cáo cá nhân: `report/team/2A202603810_PhanTranManhCuong.md`.
- Test suite: `src/tests/test_handoff_security.py` (5/5 passed), 62/62 student tests của Shape C passed.

## 2A202603802_TranPhamMinhSon

### Phần việc phụ trách

- Kiểm tra và xác nhận tính bền vững (`durability`), cơ chế idempotency (`refund:{claim_id}`), truyền `crash_at` và lan truyền ngoại lệ `InjectedCrash` trên cả ba shape.
- Đối chiếu phản ví dụ `lab8.demo.buggy_workflow` để kiểm chứng lý do checkpoint đơn lẻ không thay thế được ledger giao dịch SQLite.
- Viết test kiểm thử idempotency và crash recovery tại `src/tests/test_durability_recovery.py`.
- Hoàn thiện báo cáo cá nhân `report/team/2A202603802_TranPhamMinhSon.md`.

### Đóng góp cụ thể

- Xác nhận cả 3 shape gọi `issue_refund(conn, claim_id, proposal, crash_at=crash_at)` và re-raise `InjectedCrash` sau khi ghi trace.
- Kiểm tra tính bất biến của ledger giao dịch SQLite với `BEGIN IMMEDIATE`, khóa idempotency `refund:{claim_id}` và trần bồi thường theo đơn hàng (`per-order cap`).
- Thực thi và kiểm chứng phản ví dụ `buggy_workflow`.
- Viết 21 test cases trong `src/tests/test_durability_recovery.py` kiểm thử toàn diện idempotency, 3 điểm crash × 3 shape, amount conflict và per-order cap.

### Bằng chứng

- Commit: `9f2fb18` (nhánh `sontpm`).
- File báo cáo cá nhân: `report/team/2A202603802_TranPhamMinhSon.md`.
- Test suite: `src/tests/test_durability_recovery.py` (21/21 passed).
