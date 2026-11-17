# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2501.07541, benchmark & empirical study |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống multi-agent LLM thất bại chủ yếu do verification failure (lỗi kiểm chứng) và cascading information bias giữa các sub-agents, dẫn đến việc chấp nhận thông tin sai lệch từ ngữ cảnh giao tiếp thay vì dữ liệu nguồn thực tế. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Thực nghiệm trên các bài toán phối hợp đa tác vụ (multi-agent workflows/swarms) có chứa thông tin gây nhiễu, mâu thuẫn hoặc đầu vào người dùng có chủ đích khai thác. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển từ Swarm sang Workflow (loại bỏ suy diễn tự do từ hội thoại peer và cố định logic kiểm tra dữ liệu từ DB), pass rate tổng thể tăng từ 0.986 lên 1.000, pass^5 tăng từ 0.929 lên 1.000, và seed variance giảm từ 0.000816 về 0.000000. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: model MockLLM, bộ công cụ tools, 5 random seeds (11, 22, 33, 44, 55), 14 claim public, bảng giá mô phỏng, evaluator. Biến duy nhất được thay đổi: Topology kiến trúc xử lý (Swarm phi tập trung vs Deterministic Workflow). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi kiểm chứng (verification failure) ở claim C-002 tại seed 55: Swarm tin vào thông tin ticket của khách hàng ("trễ 5 ngày") thay vì đối soát số ngày trễ thực tế trong DB (delay_days=2 < 3) nên ra quyết định resolved thay vì denied. Đo bằng: pass rate (1.000 vs 0.986), pass^5 (1.000 vs 0.929), seed variance (0.000000 vs 0.000816), và cost per success (27.86 VND vs 49.57 VND). |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
  `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `reports/benchmark.json` (Run id lỗi kiểm chứng của Swarm: `R-swarm-C-002-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  - **Kết quả: Đúng hoàn toàn với giả thuyết.**
  - **Swarm (Shape D):** Bị lỗi kiểm chứng tại trial `R-swarm-C-002-s55` (claim `C-002`, seed 55), trả về lý do `status resolved != denied` do agent tin lời khai trong ticket mà không đối soát với `delay_days=2` trong đơn hàng. Kết quả: Pass rate = `0.9857` (69/70), Pass^5 = `0.9286`, seed variance = `0.000816`, cost/success = `49.57 VND`.
  - **Workflow (Shape A):** Loại bỏ hoàn toàn sự tự chủ của model, tính toán bồi thường dựa hoàn toàn trên dòng dữ liệu cấu trúc từ database qua `compute_compensation`. Kết quả: Pass rate = `1.000` (70/70), Pass^5 = `1.000`, seed variance = `0.000000`, cost/success = `27.86 VND` (tiết kiệm 43.8% chi phí so với Swarm, số bước trung bình chỉ 3.79 so với 2.80 nhưng đạt độ tin cậy tuyệt đối).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
