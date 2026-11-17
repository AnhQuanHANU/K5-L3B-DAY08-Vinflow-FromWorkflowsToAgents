# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: d4ccefb
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0-1.0 / 0.0
- Cost per success (mô phỏng, VND): 27.86 (simulated_not_real_api_price, 1950.0 VND / 70 trials)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 (src/reports/hidden_selfcheck.json: 0 leak_suspect / 200 trials; 128/128 host+team tests & 248/248 student matrix tests pass)

## Vì sao shape này

Trên cùng tập `data/public_claims.jsonl` (14 claim × 5 seed `11,22,33,44,55` = 70 trials/shape trong `src/reports/benchmark.json`), `workflow` đạt **pass rate 1.0**, **pass^5 = 1.0**, **seed variance = 0.0**, chi phí mô phỏng thấp nhất (**27.86 VND/success**, `0` lần gọi model, trung bình `3.79` steps), trong khi `single` tốn **46.48 VND/success** (`8.07` steps), `orchestrator` tốn **57.19 VND/success** (`5.36` steps), và `swarm` chỉ đạt **0.9857** (`pass^5 = 0.9286`, fail ở seed 55 tại `T02` vì tin số ngày trễ trong ticket) với chi phí **49.57 VND/success**. Quy trình xử lý claim của LogiX-VN đã có luật nghiệp vụ và schema rõ ràng nên `workflow` là kiến trúc ít tự chủ nhất mà vẫn giải quyết trọn vẹn bài toán.

## Có đáng đổi lấy multi-agent không

**Không.** Với bài toán hiện tại, các kiến trúc nhiều bước tự chủ hoặc multi-agent (`orchestrator`, `swarm`) làm tăng chi phí mỗi lần thành công lên gần gấp đôi (`57.19` và `49.57` so với `27.86` VND) và đưa thêm rủi ro dao động theo seed (như `swarm` bị sai ở `seed % 5 == 0`) mà không mang lại lợi thế về pass rate. Quyết định này chỉ đảo ngược khi dữ liệu đầu vào trở nên phi cấu trúc hoàn toàn (ví dụ ticket không gắn `order_id` có cấu trúc, cần suy luận đa bước từ ảnh/chứng từ hoặc phối hợp nhiều hệ thống ngoài) khiến luồng `if/else` cố định không còn bao phủ được.

## Trace và bằng chứng

Trace (`src/traces/<run_id>.json`) chỉ ghi các event đã qua lọc an toàn: `claim_lookup` (chỉ ghi `found`, `claim_id`, `has_order_id`), `order_lookup` (qua `lookup_order` với allowlist `ORDER_FIELDS`), `quote` (output của `compute_compensation`), `refund` (`ok`, `conflict`, `reason`), `crash` (khi gặp `InjectedCrash`), và `decision`. Các field nhạy cảm như `parent_secret` (`CANARY_SECRET_*`), `phone`, `address`, `item_name`, `internal_note` và `raw_headers_json` cố ý **không** được đọc bằng `SELECT *` hay ghi vào trace/stdout để giữ ranh giới bảo mật. Nếu trace nằm ngoài thư mục scanner quét, hệ thống kiểm tra sẽ đánh fail-closed (`missing_trace`), do đó mọi nhánh return và crash đều bắt buộc flush file `<run_id>.json` qua `Trace.write()`.

## Giới hạn

MockLLM không phải model sản xuất nên chỉ phản ánh hành vi và giá mô phỏng (`cost_note: simulated_not_real_api_price`), chưa đo được năng lực hiểu ngôn ngữ tự nhiên thực tế của LLM thật. Giá trị latency là `unavailable`, chưa đo được độ trễ mạng/suy luận thực tế. Tập public chỉ gồm 14 claim (70 trials/shape), nên cần kết hợp thêm tự kiểm trên 40 claim hidden (`src/reports/hidden_selfcheck.json`: 0 errors, 0 `leak_suspect`) và bài chấm hidden chính thức của giảng viên.
