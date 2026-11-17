# Team

## Thông tin nhóm

- Tên nhóm: Vinflow
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Vinflow-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: https://github.com/AnhQuanHANU/K5-Day8-Vinflow-From-Workflows-to-Agents, main

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Anh Quân | 2A202603892 | - | AnhQuanHANU | Integration & Coordination Lead (Role 1) |
|   2 | Nguyễn Đình Nam | 2A202603797 | - | dinhnam269 | Workflow Engineer (Role 2) |
|   3 | Hồ Anh Tú | 2A202603811 | - | TuHoAnh | Single Agent Engineer (Role 3) |
|   4 | Phan Trần Mạnh Cường | 2A202603810 | - | Cuongngucute | Orchestrator & Security Lead (Role 4) |
|   5 | Trần Phạm Minh Sơn | 2A202603802 | - | sontpm | Durability & Evaluation Lead (Role 5) |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Anh Quân | Integration & Coordination Lead | 27def93 | `src/tests/test_integration_smoke.py` |
| Nguyễn Đình Nam | Workflow Engineer | pending_cp2 | `src/tests/test_workflow_edge.py` |
| Hồ Anh Tú | Single Agent Engineer | pending_cp2 | `src/tests/test_single_prompt_safety.py` |
| Phan Trần Mạnh Cường | Orchestrator & Security Lead | pending_cp2 | `src/tests/test_handoff_security.py` |
| Trần Phạm Minh Sơn | Durability & Evaluation Lead | pending_cp3 | `src/tests/test_durability_recovery.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/team/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/2A202603892_NguyenAnhQuan.md`.

---

## 2A202603892_NguyenAnhQuan

### Phần việc phụ trách

- Quản lý repo, môi trường, điều phối tiến độ Checkpoints CP1–CP5.
- Cài đặt bài test tích hợp `src/tests/test_integration_smoke.py`.
- Tổng hợp báo cáo nhóm `report/team/group_report.md` và kiểm tra nộp bài `check_submission`.

### Đóng góp cụ thể

- Hoàn thành thiết lập CP1: xác thực smoke test và 54 host tests xanh 100%.
- Cấu hình phân công vai trò 5 thành viên trong nhóm Vinflow.
- Viết test suite tích hợp đảm bảo môi trường runner đồng nhất.

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603892_NguyenAnhQuan.md`.
- Test suite: `src/tests/test_integration_smoke.py`.

---

## 2A202603797_NguyenDinhNam

### Phần việc phụ trách

- Cài đặt Shape A (`src/lab8/shapes/workflow.py`).

### Đóng góp cụ thể

- (Chờ thành viên cập nhật sau khi hoàn thành CP2)

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603797_NguyenDinhNam.md`.

---

## 2A202603811_HoAnhTu

### Phần việc phụ trách

- Cài đặt Shape B (`src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- (Chờ thành viên cập nhật sau khi hoàn thành CP2)

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603811_HoAnhTu.md`.

---

## 2A202603810_PhanTranManhCuong

### Phần việc phụ trách

- Cài đặt Shape C (`src/lab8/shapes/orchestrator.py`) và bảo mật Handoff.

### Đóng góp cụ thể

- (Chờ thành viên cập nhật sau khi hoàn thành CP2 & CP3)

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603810_PhanTranManhCuong.md`.

---

## 2A202603802_TranPhamMinhSon

### Phần việc phụ trách

- Durability (`durability.py`), Crash suite 20/20, Benchmark và hồ sơ ADR/Research Card.

### Đóng góp cụ thể

- (Chờ thành viên cập nhật sau khi hoàn thành CP4 & CP5)

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603802_TranPhamMinhSon.md`.
