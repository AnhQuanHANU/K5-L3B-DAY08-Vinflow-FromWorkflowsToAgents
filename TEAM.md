# Team

## Thông tin nhóm

- Tên nhóm: Vinflow
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Vinflow-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: https://github.com/AnhQuanHANU/K5-Day8-Vinflow-From-Workflows-to-Agents, main

## Thành viên

| STT | Họ tên          | MSSV        | Email | GitHub      | Vai trò                                  |
| --: | --------------- | ----------- | ----- | ----------- | ---------------------------------------- |
|   1 | Nguyễn Anh Quân | 2A202603892 | -     | AnhQuanHANU | Integration & Coordination Lead (Role 1) |
|   2 |                 |             |       |             |                                          |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người           | Vai                             | Commit  | Test đã thêm hoặc sửa                 |
| --------------- | ------------------------------- | ------- | ------------------------------------- |
| Nguyễn Anh Quân | Integration & Coordination Lead | 27def93 | `src/tests/test_integration_smoke.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603892_NguyenAnhQuan

### Phần việc phụ trách

- Quản lý repo, môi trường, điều phối tiến độ Checkpoints CP1–CP5.
- Cài đặt bài test tích hợp `src/tests/test_integration_smoke.py`.
- Tổng hợp báo cáo nhóm `report/team/group_report.md` và kiểm tra nộp bài `check_submission`.

### Đóng góp cụ thể

- Hoàn thành thiết lập CP1: xác thực smoke test và 54 host tests xanh 100%.
- Cấu hình phân công vai trò nhóm Vinflow.
- Viết test suite tích hợp đảm bảo môi trường runner đồng nhất.

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603892_NguyenAnhQuan.md`.
- Test suite: `src/tests/test_integration_smoke.py`.

## 2A202603811_HoAnhTu

### Phần việc phụ trách

- Cài đặt toàn bộ Shape B (Single ReAct Agent) tại `src/lab8/shapes/single.py`.
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
- Test suite: `src/tests/test_single_prompt_safety.py` (3/3 passed), 62/62 test student của Shape B passed, và 57 host tests passed.
