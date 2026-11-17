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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* (https://arxiv.org/abs/2503.13657), benchmark & human annotation taxonomy (κ = 0.88). |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Các hệ thống multi-agent LLM thường thất bại ở 3 nhóm chính: lỗi thiết kế hệ thống, lệch phối hợp giữa các agent (inter-agent misalignment), và lỗi kiểm chứng nhiệm vụ (task verification). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Phân loại rút ra từ 7 framework MAS mã nguồn mở trên hơn 1600 trace; chưa trực tiếp kiểm chứng trên hệ thống có Host cưỡng chế luật bằng code cứng như LogiX-VN. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ `workflow` (không gọi model đọc ticket) sang `swarm` (có peer/parse LLM trên ticket), pass rate và `pass^5` sẽ giảm ở các seed bị nhiễu (seed % 5 == 0) do lỗi kiểm chứng dữ liệu, đồng thời `cost/success` tăng khoảng 1.7–1.8×. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tools (`compute_compensation`, `issue_refund`), 5 seeds (`11,22,33,44,55`), corpus `data/public_claims.jsonl` (14 claims), bảng giá và evaluator. Biến duy nhất thay đổi: kiến trúc (`workflow` vs `swarm`). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: `swarm` tin số ngày trễ viết trong ticket ở seed 55 (`T02`, dẫn tới `status resolved != denied` — thuộc nhóm lỗi kiểm chứng dữ liệu). Đo bằng `pass_rate`, `pass^5`, `seed_variance`, `cost_per_success_vnd` và `reasons`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11` (và `R-swarm-C-002-s55`) trong `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng với giả thuyết.** `workflow` đạt `pass_rate = 1.0`, `pass^5 = 1.0`, `seed_variance = 0.0`, `cost_per_success_vnd = 27.86 VND`; trong khi `swarm` đạt `pass_rate = 0.9857` (69/70), `pass^5 = 0.9286`, `seed_variance = 0.000816`, `cost_per_success_vnd = 49.57 VND` (gấp 1.78×), fail 1 trial ở seed 55 với lý do `status resolved != denied`.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
