# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 24ea589
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng tập corpus public (14 claim) và 5 seed kiểm thử (11, 22, 33, 44, 55, tổng 70 trials per shape), Shape A (`workflow`) đạt pass rate tuyệt đối 1.000, pass^5 đạt 1.000 và seed variance bằng 0.000000. Đây là kiến trúc có mức độ tự chủ thấp nhất (least autonomous) nhưng mang lại hiệu quả kinh tế vượt trội nhất: chi phí mô phỏng chỉ 27.86 VND/thành công (thấp hơn 40% so với single: 46.48 VND, thấp hơn 51% so với orchestrator: 57.19 VND, và thấp hơn 43.8% so với swarm: 49.57 VND) với số bước thực thi trung bình ngắn nhất (3.79 steps). Bài toán bồi thường LogiX-VN có luật kinh doanh hoàn toàn xác định (`docs/business_rules.md`). Việc đưa LLM vào tự chủ ra quyết định hay để các agent trao đổi tự do (như Swarm) không đem lại bất kỳ cải thiện nào về nghiệp vụ, ngược lại còn dẫn đến lỗi kiểm chứng (Swarm fail C-002 ở seed 55 do tin lời ticket thổi phồng số ngày trễ) và nguy cơ bị tấn công prompt injection. Do đó, Shape A là lựa chọn an toàn, bền bỉ và tối ưu chi phí nhất cho môi trường sản xuất.

## Có đáng đổi lấy multi-agent không

Nhóm khẳng định là **hoàn toàn không đáng đổi**. Thực nghiệm đo lường cho thấy multi-agent (Swarm) không những không nâng cao tỷ lệ giải quyết thành công mà còn làm giảm độ tin cậy: pass rate chỉ đạt 0.986, pass^5 tụt xuống 0.929, variance tăng lên 0.000816 (do trượt claim C-002 ở seed 55 vì cascading bias), trong khi chi phí bồi thường tăng vọt thêm 78% (49.57 VND so với 27.86 VND của workflow). Quyết định chỉ đáng đảo lại sang multi-agent (Orchestrator hoặc Swarm) khi thỏa mãn đồng thời 3 điều kiện: (1) Nghiệp vụ khiếu nại mở rộng sang dữ liệu phi cấu trúc phức tạp (phân tích ảnh hàng hỏng, thẩm định biên bản giao nhận nhiều bên, thương lượng ngoại lệ) mà luồng deterministic code không thể bao quát; (2) Có cơ chế automated verifier độc lập và bảo vệ dữ liệu nghiêm ngặt giữa các sub-agents để triệt tiêu hiện tượng verification failure; (3) Lợi ích kinh tế từ các ca khiếu nại phức tạp được giải quyết thành công vượt trội hoàn toàn chi phí token và rủi ro phương sai (variance) của mô hình.

## Trace và bằng chứng

Trace của nhóm ghi nhận đầy đủ các sự kiện nghiệp vụ theo đúng Trace contract v1: `claim` (chỉ ghi cờ `has_order_id`), `investigator`/`order` (chỉ ghi nhận các trường dữ liệu hợp lệ trong allowlist `ORDER_FIELDS`: `order_id`, `status`, `shipping_fee`, `delay_days`, `policy_code`), `quote` (số tiền bồi thường tính toán từ code), `host` (kết quả phê duyệt và ghi sổ từ host durability), `crash` (khi gặp ngoại lệ mô phỏng `InjectedCrash`), và `decision` (`status`, `amount`, `resolution`).
Các trường cố ý **không** ghi: `ticket` (chứa văn bản người dùng nhập tự do, có rủi ro prompt injection và PII), `principal_id`, `parent_secret`, `CANARY_SECRET_*`, `raw_headers_json`, số điện thoại, địa chỉ nhận hàng, `internal_note`, và `item_name`.
Đội ngũ security chứng minh hệ thống không rò rỉ secret thông qua:
1. **Kiến trúc cô lập dữ liệu (View Isolation):** Hàm `get_claim_view` và `lookup_order` chỉ đọc các cột cần thiết, tuyệt đối không nạp `parent_secret` hay `raw_headers_json` vào context xử lý.
2. **Bộ lọc Allowlist:** Chỉ serialize các field được chỉ định rõ trong `ORDER_FIELDS` vào trace.
3. **Phòng thủ SafeTrace:** Tự động bắt và thay thế mọi chuỗi chứa marker canary secret thành `{"redacted": true}`.
4. **Kiểm thử tự động:** Test suite `src/tests/test_handoff_security.py` quét toàn bộ trace qua biểu thức chính quy trên 14 claim public × 5 seed, xác nhận 0 rò rỉ bí mật và 0 bypass phê duyệt (`Secret leak / approval bypass: 0 / 0`).

## Giới hạn

Thực nghiệm sử dụng MockLLM với các kịch bản seed ngẫu nhiên nhằm mô phỏng hành vi suy luận, chưa phản ánh đầy đủ độ trễ mạng thực tế (trường latency hiển thị `unavailable`) cũng như các kỹ thuật prompt injection nhiều bước tinh vi của môi trường sản xuất thực tế. Chi phí tính toán là chi phí quy đổi mô phỏng trong đề bài, không đại diện cho giá token thương mại trực tiếp. Toàn bộ số liệu trong báo cáo được trích xuất trực tiếp từ các công cụ chuẩn `lab8.benchmark` và `lab8.crash_test`, tuyệt đối tuân thủ quy định không can thiệp hay sửa đổi file JSON kết quả.
