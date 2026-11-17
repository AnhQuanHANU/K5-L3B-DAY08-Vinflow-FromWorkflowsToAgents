# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: Vinflow
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Vinflow-FromWorkflowsToAgents` (GitHub: `https://github.com/AnhQuanHANU/K5-Day8-Vinflow-From-Workflows-to-Agents`)
- Thành viên: xem `TEAM.md` (gồm 5 thành viên: Nguyễn Anh Quân, Nguyễn Đình Nam, Hồ Anh Tú, Phan Trần Mạnh Cường, Trần Phạm Minh Sơn)
- Commit chốt (trùng `report/team/decision_adr.md`): `24ea589`

## 2. Mục tiêu và cách tiếp cận

### 2.1. Hiểu bài toán
Hệ thống giải quyết bài toán tự động xử lý khiếu nại bồi thường đơn hàng thương mại điện tử (LogiX-VN). Thách thức cốt lõi không chỉ nằm ở việc tính toán bồi thường theo đúng luật kinh doanh (`docs/business_rules.md`) mà còn là bảo vệ an toàn trước các cuộc tấn công prompt injection qua ticket người dùng, đảm bảo tính bền vững (durability), chống gian lận/hoàn tiền kép khi crash (idempotency), và cô lập dữ liệu nhạy cảm (PII, canary secrets).

### 2.2. Phân chia công việc và thứ tự làm 4 shape
Nhóm phân công độc lập 5 vai trò theo đúng năng lực và kịch bản chuẩn:
- **Thành viên 1 (Nguyễn Anh Quân — Role 1):** Integration & Coordination Lead — Khởi tạo môi trường, thiết lập Git workflow, viết `test_integration_smoke.py`, điều phối checkpoints và tổng hợp báo cáo.
- **Thành viên 2 (Nguyễn Đình Nam — Role 2):** Workflow Engineer — Phụ trách Shape A (`workflow.py`), test biên `test_workflow_edge.py`.
- **Thành viên 3 (Hồ Anh Tú — Role 3):** Single Agent Engineer — Phụ trách Shape B (`single.py`), test an toàn prompt injection `test_single_prompt_safety.py`.
- **Thành viên 4 (Phan Trần Mạnh Cường — Role 4):** Orchestrator & Security Lead — Phụ trách Shape C (`orchestrator.py`), kiểm soát handoff và trace bảo mật trong `test_handoff_security.py`.
- **Thành viên 5 (Trần Phạm Minh Sơn — Role 5):** Durability & Evaluation Lead — Kiểm chứng ledger, crash safety, viết `test_durability_recovery.py`, chạy benchmark và phân tích ADR.

**Thứ tự triển khai:**
1. **CP1:** Chốt contracts, chạy smoke test, bảo vệ 54 bài test của cổng host và xác lập baseline.
2. **CP2:** Cài đặt độc lập 3 shape nhóm viết (`workflow`, `single`, `orchestrator`) trên các nhánh git riêng biệt, đảm bảo vượt qua 62 bài test student cho mỗi shape.
3. **CP3:** Tích hợp cơ chế durability, truyền `crash_at` vào `durability.issue_refund`, re-raise `InjectedCrash` và ghi trace sự kiện crash.
4. **CP4:** Chạy kiểm thử crash safety tự động với 20 kịch bản ngẫu nhiên (`src/reports/crash.json`), đạt chuẩn tuyệt đối 20/20.
5. **CP5:** Thực hiện benchmark toàn diện 4 shape × 14 claim × 5 seed (`src/reports/benchmark.json`), thực hiện ablation R2, viết ADR lựa chọn kiến trúc tối ưu và hoàn thiện toàn bộ tài liệu nộp bài.

## 3. Giải pháp

### 3.1. Shape A: Deterministic Workflow (`src/lab8/shapes/workflow.py`)
- **Nguyên lý:** Xử lý bằng mã nguồn Python thuần túy theo đồ thị quyết định xác định, không gọi LLM suy diễn.
- **Đọc dữ liệu:** Gọi `get_claim_view` và `lookup_order` chỉ lấy các trường cần thiết; tuyệt đối không dùng `SELECT *` để ngăn chặn nạp `parent_secret` hay `raw_headers_json`.
- **Quyết định & Tính toán:** Tính bồi thường qua `compute_compensation(conn, order)` trực tiếp trên dữ liệu DB. Bỏ qua số ngày trễ ghi trong ticket người dùng, loại bỏ hoàn toàn nguy cơ prompt injection và đạt variance = 0.
- **Tương tác Host:** Khi `quote > 0`, gọi `durability.issue_refund(conn, claim_id, quote, crash_at=crash_at)` với **quote đầy đủ** để Host tự kiểm duyệt approval và khấu trừ lịch sử hoàn tiền (tránh lỗi trừ 2 lần ở T14). Bắt `InjectedCrash` ghi trace rồi re-raise. Trả kết quả qua `common.finish()`.

### 3.2. Shape B: Single ReAct Agent (`src/lab8/shapes/single.py`)
- **Nguyên lý:** Vòng lặp ReAct suy luận đa bước sử dụng `lab8.runtime.run_react` với giới hạn cứng `max_steps=8` và cờ `worker=True`.
- **Phân quyền công cụ:** Chỉ cấp các tool đọc (`get_claim_view`, `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`). Chặn hoàn toàn `issue_refund` trong vòng lặp agent; hành vi cố tình gọi write tool sẽ bị ném `ToolRejected`.
- **Ranh giới an toàn:** Dữ liệu sự thật luôn lấy từ DB qua `lookup_order`. Quyết định ghi tiền bồi thường chỉ được thực hiện ở tầng host sau khi agent kết thúc vòng lặp.
- **Trace:** Ghi nhận theo Trace contract v1, không ghi ticket thô hay thông tin nhạy cảm.

### 3.3. Shape C: Orchestrator-Workers (`src/lab8/shapes/orchestrator.py`)
- **Nguyên lý:** Mô hình điều phối trung tâm chia tách nhiệm vụ thành các sub-task độc lập cho investigator.
- **Ranh giới Code / Model:** MockLLM chỉ đảm nhiệm lập kế hoạch (`plan`) và soạn thảo phản hồi (`draft`). Toàn bộ logic tính toán tiền và kiểm tra điều kiện chuyển tiếp thuộc về deterministic code.
- **Handoff Sanitized (`handoff.v1`):** Khởi tạo handoff bằng `make_handoff` với `facts={}` và chỉ cấp 4 read-only tools. Context của parent (ticket, secret, header) bị chặn hoàn toàn không cho đi qua ranh giới handoff sang worker.
- **Lớp bảo vệ SafeTrace:** Kế thừa `Trace`, chủ động quét và thay thế mọi chuỗi chứa `CANARY_SECRET_*`, `parent_secret` hoặc marker bí mật thành `{"redacted": true}`.

### 3.4. Durability & Idempotency
- Áp dụng giao dịch SQLite `BEGIN IMMEDIATE` tại `durability.issue_refund`. Khóa idempotency `refund:{claim_id}` đảm bảo an toàn tuyệt đối khi gọi lại nhiều lần hoặc resume sau crash ở cả 3 điểm (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`).
- Duy trì trần bồi thường theo đơn hàng (`per-order cap`), chống ghi thừa khi bù tiền đơn hàng (`topup`).

## 4. Kết quả

### 4.1. Bảng so sánh 4 shape trên bộ dữ liệu public
Số liệu trích xuất chính thức từ `src/reports/benchmark.json` (70 trials mỗi shape: 14 claims × 5 seeds [11, 22, 33, 44, 55]):

| Shape | Pass rate | Pass^5 | Seed min–max | Seed variance | Cost/success (VND) | Mean steps | P95 steps | Mean Model calls | Mean Tool calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **workflow** | **1.000** | **1.000** | **1.000 – 1.000** | **0.000000** | **27.86** | **3.79** | **4.0** | **0.0** | **2.79** |
| single | 1.000 | 1.000 | 1.000 – 1.000 | 0.000000 | 46.48 | 8.07 | 9.0 | 2.0 | 4.50 |
| orchestrator | 1.000 | 1.000 | 1.000 – 1.000 | 0.000000 | 57.19 | 5.36 | 6.0 | 2.0 | 5.57 |
| swarm | 0.986 | 0.929 | 0.929 – 1.000 | 0.000816 | 49.57 | 2.80 | 3.0 | 3.0 | 4.66 |

### 4.2. Kết quả kiểm thử Crash Safety
- Chạy từ công cụ `lab8.crash_test` xuất ra `src/reports/crash.json`:
  - **Crash safety:** **20/20 (100% passed)**
  - Đã kiểm tra đầy đủ 3 điểm inject crash: `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`, cùng các kịch bản `amount_conflict_on_retry`, `retry_without_approval`, và `swarm_after_effect_before_checkpoint`. Không có bất kỳ trường hợp nào bị chi trả trùng lặp (double refund).

### 4.3. Quyết định kiến trúc (ADR) và Nghiên cứu Ablation
- **Quyết định chọn:** Shape A (`workflow`) được chọn làm kiến trúc triển khai chính thức (xem chi tiết tại `report/team/decision_adr.md`).
  - *Lý do:* Đạt độ chính xác tuyệt đối (Pass^5 = 1.000), phương sai bằng 0, không phụ thuộc LLM, và có chi phí vận hành rẻ nhất (27.86 VND/thành công).
- **Ablation R2 (MAST, NeurIPS 2025):** Xem chi tiết tại `report/team/research_card.md`. Swarm thất bại ở claim C-002 seed 55 do lỗi kiểm chứng (verification failure), tin vào lời ticket thổi phồng thay vì số liệu thực trong DB. Chuyển sang Workflow giúp triệt tiêu hoàn toàn lỗi này.

## 5. Khó khăn và cách xử lý

1. **Lỗi nuốt ngoại lệ khi xử lý Crash ở Shape A (T12):**
   - *Hiện tượng:* Ban đầu trong `workflow.py` dùng `del crash_at` thay vì chuyển tham số, khiến test `test_t12_crash_before_checkpoint_does_not_double_pay` bị fail do không kích hoạt được crash injected.
   - *Xử lý:* Sửa lại thành `outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)` và bọc khối `try...except InjectedCrash:` ghi sự kiện `"crash"` vào trace rồi re-raise ngoại lệ. Kết quả vượt qua 62/62 student tests.
2. **Lỗi trừ tiền hai lần ở đơn bù (T14 - Topup Refund):**
   - *Hiện tượng:* Khi khiếu nại trước đã được hoàn một phần, nếu shape tự trừ số tiền đã hoàn trước khi gọi `issue_refund`, host sẽ trừ tiếp một lần nữa dẫn đến số tiền bồi thường bị giảm sai lệch (ra 90.000 VND thay vì 120.000 VND).
   - *Xử lý:* Cả 3 shape đều tuân thủ truyền **quote đầy đủ** (toàn bộ hạn mức bồi thường của đơn), để tầng host tự động truy vấn lịch sử `refund_ledger` và khấu trừ chính xác trong cùng transaction.
3. **Quản lý rò rỉ dữ liệu nhạy cảm và Canary Secrets qua Handoff/Trace:**
   - *Hiện tượng:* Context cha chứa các header và secret có thể bị lan truyền sang sub-agents hoặc ghi vào file trace nếu không kiểm soát chặt.
   - *Xử lý:* Áp dụng triệt để Allowlist Sanitization (`handoff.v1`), chỉ truyền dict rỗng `facts={}` qua handoff và xây dựng lớp `SafeTrace` tự động che giấu các chuỗi marker bí mật.

## 6. Tổng hợp đóng góp

| STT | Thành viên | Vai trò | Commit chính | Module phụ trách | Test đã thêm / sửa |
| :--: | :--- | :--- | :---: | :--- | :--- |
| 1 | Nguyễn Anh Quân | Integration & Coordination Lead | `27def93` | Điều phối tổng thể CP1–CP5, thiết lập môi trường, tổng hợp báo cáo | `src/tests/test_integration_smoke.py` |
| 2 | Nguyễn Đình Nam | Workflow Engineer | `4481fbf` | Cài đặt toàn bộ Shape A (`workflow.py`), xử lý CP2, CP3 | `src/tests/test_workflow_edge.py` |
| 3 | Hồ Anh Tú | Single Agent Engineer | `7488543` | Cài đặt toàn bộ Shape B (`single.py`), ReAct an toàn | `src/tests/test_single_prompt_safety.py` |
| 4 | Phan Trần Mạnh Cường | Orchestrator & Security Lead | `0009e06` | Cài đặt toàn bộ Shape C (`orchestrator.py`), SafeTrace, Allowlist handoff | `src/tests/test_handoff_security.py` |
| 5 | Trần Phạm Minh Sơn | Durability & Evaluation Lead | `9f2fb18` | Kiểm thử durability, idempotency, benchmark 4 shape, ADR analysis | `src/tests/test_durability_recovery.py` |

*Chi tiết báo cáo cá nhân của từng thành viên xem tại `report/team/2A202603892_NguyenAnhQuan.md`, `report/team/2A202603797_NguyenDinhNam.md`, `report/team/2A202603811_HoAnhTu.md`, `report/team/2A202603810_PhanTranManhCuong.md`, và `report/team/2A202603802_TranPhamMinhSon.md`.*

## 7. Hạn chế và hướng cải thiện

- **Hạn chế:**
  - Môi trường thử nghiệm sử dụng MockLLM với các kịch bản phản hồi định sẵn, chưa đo lường được độ trễ mạng thực tế (trường `latency` ghi nhận `unavailable`) cũng như sự biến động về ngữ nghĩa của các mô hình ngôn ngữ lớn thương mại thực tế.
  - Bộ dữ liệu đánh giá public gồm 14 ca khiếu nại, chưa phản ánh hết các tình huống tranh chấp phức tạp đa tài liệu hoặc gian lận có tổ chức.
- **Hướng cải thiện:**
  - Tích hợp các LLM production thực tế (như Gemini 1.5 Pro, Claude 3.5 Sonnet) với cơ chế fallback tự động về Deterministic Workflow khi phát hiện prompt injection hoặc bất thường về chi phí.
  - Mở rộng kiến trúc bền vững từ SQLite đơn máy sang cơ chế phân tán (Distributed Transaction Ledger với PostgreSQL hoặc CockroachDB) có hỗ trợ 2-phase commit và distributed locking (Redlock).

## 8. Tài liệu tham khảo

1. MAST Team. (2025). *Why Do Multi-Agent LLM Systems Fail?* NeurIPS 2025. arXiv:2501.07541.
2. Google Research. (2026). *Towards a Science of Scaling Agent Systems*.
3. Yao, S., et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023.
4. Tài liệu đặc tả kỹ thuật dự án LogiX-VN: `docs/contracts.md`, `docs/business_rules.md`, `docs/architecture.md`.
