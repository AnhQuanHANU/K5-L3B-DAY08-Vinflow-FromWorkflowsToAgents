# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: Vinflow (Lớp L3B)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `f6093d5` (cập nhật hash mới nhất sau khi commit báo cáo CP5)

## 2. Mục tiêu và cách tiếp cận

Bài lab yêu cầu xây dựng hệ thống xử lý claim hoàn phí vận chuyển và bồi thường hư hỏng cho công ty giả lập LogiX-VN trên 4 kiến trúc có mức độ tự chủ tăng dần (`workflow`, `single`, `orchestrator`, `swarm`) với cùng chữ ký `run_claim` và cùng cổng kiểm duyệt Host. Nhóm chia vai theo từng shape và phần tích hợp/bảo mật:
- Thiết lập cổng host và tích hợp kiểm thử chung.
- Cài đặt độc lập 3 shape: Shape A (`workflow`), Shape B (`single`), Shape C (`orchestrator`), đối chứng với Shape D (`swarm` tham chiếu).
- Kiểm thử an toàn crash (`crash_test`), rà soát rò rỉ secret/PII và chạy benchmark trên 5 seed (`11,22,33,44,55`) để ra quyết định kiến trúc dựa trên số liệu.

## 3. Giải pháp

Cả ba shape nhóm cài đặt đều tuân thủ ranh giới code/model: **tiền bồi thường do `compute_compensation` tính**, **quyền duyệt, trần theo đơn và idempotency (`refund:{claim_id}`) do `durability.issue_refund` kiểm soát**, model chỉ làm nhiệm vụ điều hướng tool đọc hoặc soạn câu chữ.
- **Shape A (`workflow` — `src/lab8/shapes/workflow.py`):** Chạy luồng Python tuần tự cố định: `get_claim_view` → kiểm `order_id` (`needs_info`) → `lookup_order` (`escalated` nếu ngoài phạm vi) → `compute_compensation` → `denied` nếu quote = 0, ngược lại truyền **quote đầy đủ** vào `issue_refund(..., crash_at=crash_at)` và không bắt `InjectedCrash`. Không gọi MockLLM nên `model_calls = 0`.
- **Shape B (`single` — `src/lab8/shapes/single.py`):** Vòng lặp ReAct (tối đa 8 bước) chỉ cho phép gọi tool đọc, bỏ qua chữ gây nhiễu trong ticket; sau vòng lặp dùng `compute_compensation` và `issue_refund` tương tự Shape A.
- **Shape C (`orchestrator` — `src/lab8/shapes/orchestrator.py`):** Tách vai điều phối và điều tra viên; dữ kiện truyền qua `lab8.handoff.make_handoff` chỉ giữ các field trong allowlist (loại bỏ `parent_secret`, `phone`, `address`, `internal_note`, `item_name`).
- **Trace & bảo mật:** Mọi nhánh trả về (kể cả lỗi sớm và crash) đều ghi file JSON `<run_id>.json` qua `Trace.write()`, chỉ chứa dữ liệu đã sanitize.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (`src/reports/benchmark.json`, 14 claim × 5 seed `11,22,33,44,55` = 70 trials/shape):

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost / success (VND) | Mean / p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `workflow` | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 27.86 | 3.79 / 4.0 |
| `single` | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 46.48 | 8.07 / 9.0 |
| `orchestrator` | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 57.19 | 5.36 / 6.0 |
| `swarm` | 0.9857 | 0.9286 | 0.9286–1.0000 | 0.000816 | 49.57 | 2.80 / 3.0 |

- **Crash safety (`src/reports/crash.json`):** `20/20` kịch bản crash đều kết thúc với đúng 1 dòng refund và 1 audit `refund_committed`.
- **Kiểm thử tự động (`src/`):** `128 passed` (`pytest -q`) và `248 passed` (`pytest -q -m student -o addopts=`).
- **Tự kiểm bộ hidden (`src/reports/hidden_selfcheck.json`):** `workflow`, `single`, `orchestrator` chạy đủ 200 trials/shape với `0` errors, `0` bad trace và `0` `leak_suspect`.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **T12 (Crash trước checkpoint):** Ban đầu nếu không truyền `crash_at` vào `issue_refund` hoặc bắt nhầm `InjectedCrash` thì test T12 fail; nhóm đã sửa để truyền thẳng `crash_at` và chỉ flush `trace.write()` trước khi `raise` lại `InjectedCrash`.
- **T13 / T14 (Trần hoàn tiền theo đơn):** Nếu shape tự trừ số tiền đã hoàn trước đó rồi mới gọi `issue_refund` thì Host sẽ trừ thêm lần nữa; nhóm thống nhất luôn truyền quote đầy đủ từ `compute_compensation` vào `issue_refund`.
- **Xung đột merge file `src/reports/crash.json` untracked:** Khi kéo code từ `main`, xóa bản untracked cục bộ để fast-forward sạch từ `origin/main`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- **Giới hạn:** MockLLM không phải model sản xuất nên giá và độ chính xác suy luận chỉ mang tính mô phỏng; giá trị latency là `unavailable`; tập public mới có 14 claim nên cần kết hợp kết quả chấm hidden 40 claim của giảng viên.
- **Điều kiện đảo kết luận:** Nếu bài toán mở rộng sang xử lý chứng từ ảnh/hội thoại tự do không có `order_id` cấu trúc, khi đó `single` hoặc `orchestrator` có thể vượt `workflow` về độ phủ xử lý.

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md` trong repo Lab 8 LogiX-VN.
- MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?*
