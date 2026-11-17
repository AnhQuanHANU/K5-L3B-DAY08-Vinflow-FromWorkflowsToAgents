# Báo cáo cá nhân — 2A202603892_NguyenAnhQuan

## 1. Thông tin thành viên

- Họ tên: Nguyễn Anh Quân
- MSSV: 2A202603892
- Email: quan.na2A202603892@vinuni.edu.vn
- GitHub: AnhQuanHANU
- Vai trò: Integration & Coordination Lead (Role 1)
- Nhóm: Vinflow (Lớp L3B)

## 2. Phần việc phụ trách

- Quản lý repository GitHub nhóm, cấu hình môi trường runner trên Windows / Python 3.15.2.
- Điều phối tiến độ cả nhóm theo 5 checkpoints của Lab 8 (CP1 đến CP5).
- Khởi tạo tài liệu nhóm `TEAM.md`, ma trận phân công 5 thành viên và cấu trúc báo cáo.
- Xây dựng bài kiểm thử tích hợp môi trường `src/tests/test_integration_smoke.py`.
- Tổng hợp báo cáo nhóm `report/team/group_report.md` và chạy bộ kiểm tra nộp bài `check_submission`.

## 3. Đóng góp cụ thể

- **Checkpoint 1 (CP1):**
  - Chạy smoke test và xác thực 54 test của cổng host xanh tuyệt đối (`python -m pytest -q`).
  - Kiểm tra baseline student tests: 186 failed (3 stub shapes) và 62 passed (swarm reference), đúng chính xác với đặc tả đề bài.
  - Phân chia vai trò rõ ràng cho 5 thành viên trong nhóm:
    + TV1 (Nguyễn Anh Quân): Integration & Coordination Lead
    + TV2 (Nguyễn Đình Nam): Workflow Engineer (`workflow.py`)
    + TV3 (Hồ Anh Tú): Single Agent Engineer (`single.py`)
    + TV4 (Phan Trần Mạnh Cường): Orchestrator & Security Lead (`orchestrator.py`)
    + TV5 (Trần Phạm Minh Sơn): Durability & Evaluation Lead (`durability`, crash, benchmark)
  - Viết test suite `src/tests/test_integration_smoke.py` kiểm tra cấu hình môi trường, manifest và độ sẵn sàng của DB.

## 4. Bằng chứng

- Repository: `https://github.com/AnhQuanHANU/K5-Day8-Vinflow-From-Workflows-to-Agents`
- Test đã thêm: `src/tests/test_integration_smoke.py` (chạy qua pytest, commit `27def93`).
- File thông tin nhóm: `TEAM.md`.
- Kết quả smoke test CP1: `lab8.smoke pass`, `54 passed in host pytest`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (Google DeepMind Gemini).
- **Mục đích sử dụng:**
  - Hỗ trợ đọc hiểu tài liệu, luật nghiệp vụ LogiX-VN và các hợp đồng đầu ra (`RunResult`, `Trace contract v1`).
  - Hỗ trợ xây dựng kịch bản phân công công việc 5 người cân đối khối lượng và chống xung đột mã nguồn.
  - Hỗ trợ viết test suite tích hợp ban đầu.
- **Tự kiểm tra:**
  - Tự chạy `python -m lab8.smoke` và `pytest` độc lập trong terminal máy cá nhân.
  - Đối chiếu từng tiêu chí chấm trong `RUBRIC.md` và `CHECKPOINTS.md`.

## 6. Tự đánh giá

- Hoàn thành đầy đủ 100% nhiệm vụ của Checkpoint 1 độc lập.
- Sẵn sàng phối hợp và tích hợp code khi các thành viên TV2, TV3, TV4, TV5 commit các shape tương ứng.
