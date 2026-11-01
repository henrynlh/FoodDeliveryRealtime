# BÁO CÁO TIẾN ĐỘ TUẦN 4 – ĐỀ TÀI: ỨNG DỤNG GIAO ĐỒ ĂN (THEO DÕI TRẠNG THÁI THỜI GIAN THỰC)

- **Lớp học phần:** Điện toán đám mây (Cloud Computing).
- **Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng.
- **Thời gian thực hiện:** 26/10/2026 – 01/11/2026.
- **GitHub Repository (Public):** [FoodDeliveryRealtime](https://github.com/henrynlh/FoodDeliveryRealtime).
- **Kế hoạch tuần 4:** [TaskAssignments/Week_04.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/TaskAssignments/Week_04.md).
- **Video demo (Git LFS):** [demo/FoodDeliveryRealtimeDemo.mp4](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/demo/FoodDeliveryRealtimeDemo.mp4).
- **Nhật ký làm việc tuần 4 (Worklog):**
  - Trương Tấn Phát (TV1): [worklog/TanPhat/Week_04.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/worklog/TanPhat/Week_04.md).
  - Nguyễn Lê Huy (TV2): [worklog/LeHuy/Week_04.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/worklog/LeHuy/Week_04.md).
- **Kết quả kiểm thử tuần 4:** [tests/Week_04/results.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/results.md).

---

## 1. MỤC TIÊU & KẾT QUẢ ĐẠT ĐƯỢC TRONG TUẦN 4

- **Kiểm thử hồi quy toàn luồng E2E:** Hoàn tất luồng `PLACED` → `ACCEPTED` → `DELIVERING` → `COMPLETED`, đồng bộ realtime và gửi email thông báo Amazon SNS.
- **Cải tiến giao diện:** Hiển thị rõ trạng thái kết thúc (`TIMED_OUT`, `FAILED`), khóa nút thao tác và tự động dừng polling.
- **Kiểm thử riêng nhánh lỗi Commit:** Xác nhận cơ chế Catch của Step Functions bắt lỗi claim không hợp lệ và lưu `FAILED` bền vững vào DynamoDB.
- **Kiểm thử Timeout 300s & Callback trễ:** Xác nhận rẽ nhánh `HandleTimeout` → `PersistWorkflowFailure` và Lambda từ chối an toàn các yêu cầu gửi sau khi hết hạn.
- **Kiểm thử khôi phục sau CONFLICT:** Độc lập với polling, giao diện tự động bắt lỗi và đọc lại snapshot hợp lệ.
- **Kiểm thử ngắt chủ động & Reconnect:** Tự động kết nối lại khi online và khôi phục snapshot mới nhất.
- **Kiểm thử tính lũy thừa & Cạnh tranh:** Xử lý an toàn khi gửi lặp request (`ALREADY_DONE`, không tăng version) và tranh chấp 2 tài xế nhận cùng đơn (Race Condition).
- **Giám sát & Truy vết log:** Đối chiếu liên thông giữa API Gateway WebSocket và CloudWatch log của Dispatcher Lambda.
- **Video Demo hoàn chỉnh:** Hoàn thành video demo trình diễn hệ thống theo chuẩn thời lượng dưới 10 phút, lưu tại thư mục `demo/`.

---

## 2. CHI TIẾT CÔNG VIỆC VÀ LINK GITHUB TƯƠNG ỨNG

### 2.1. Trương Tấn Phát (MSSV: 24110298) – Phụ trách Backend, Workflow & Kiểm thử ngoại lệ

- **Cấu hình Step Functions Workflow Live tuần 4:**
  - Định nghĩa ASL hoàn thiện có `PersistWorkflowFailure`, `Catch` lỗi tại Commit và Timeout 300s: [config/TanPhat/Week_04/w4-workflow-live.asl.json](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/config/TanPhat/Week_04/w4-workflow-live.asl.json).
- **Xây dựng các kịch bản kiểm thử backend:**
  - Script kiểm thử riêng nhánh lỗi commit có kiểm soát: [tests/Week_04/commit_failure_probe.py](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/commit_failure_probe.py).
  - Script khởi tạo đơn kiểm thử timeout 300s tại các bước chờ: [tests/Week_04/create_timeout_order.py](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/create_timeout_order.py).
  - Script tự động chạy luồng thành công E2E: [tests/Week_04/run_e2e_order.py](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/run_e2e_order.py).
  - Script tạo đơn kiểm thử tính lũy thừa gửi lặp: [tests/Week_04/create_placed_order.py](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/create_placed_order.py).
  - Script đọc snapshot dữ liệu an toàn không lộ token: [tests/Week_04/backend_snapshot.py](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/backend_snapshot.py).
  - Script kiểm thử 2 tài xế tranh nhận đơn: [tests/Week_04/race_accept.py](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/race_accept.py).
- **Thực hiện kiểm thử và ghi nhận minh chứng backend:**
  - Bộ 21 ảnh minh chứng chi tiết và 1 tệp JSON đánh giá tự động: [evidence/TanPhat/Week_04/](https://github.com/henrynlh/FoodDeliveryRealtime/tree/main/evidence/TanPhat/Week_04).
- **Nhật ký công việc cá nhân TV1:**
  - Nhật ký làm việc tuần 4: [worklog/TanPhat/Week_04.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/worklog/TanPhat/Week_04.md).

### 2.2. Nguyễn Lê Huy (MSSV: 24110221) – Phụ trách Frontend, WebSocket & Tích hợp

- **Cập nhật và hoàn thiện giao diện tuần 4:**
  - Giao diện khách hàng: [customer.html](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/code/LeHuy/Week_04/frontend/customer.html).
  - Giao diện tài xế: [driver.html](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/code/LeHuy/Week_04/frontend/driver.html).
  - Xử lý đồng bộ WebSocket, hiển thị trạng thái kết thúc, dừng polling và khóa nút: [shared.js](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/code/LeHuy/Week_04/frontend/shared.js).
- **Kế hoạch thực hiện và tiêu chí kiểm thử:**
  - Bảng phân công và kịch bản W4-TC01 đến W4-TC09: [TaskAssignments/Week_04.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/TaskAssignments/Week_04.md).
- **Thực hiện kiểm thử giao diện, WebSocket và thu thập minh chứng:**
  - Bộ ảnh minh chứng kiểm thử giao diện khách/tài xế, timeout, reconnect, CONFLICT và log: [evidence/LeHuy/Week_04/](https://github.com/henrynlh/FoodDeliveryRealtime/tree/main/evidence/LeHuy/Week_04).
- **Nhật ký công việc cá nhân TV2:**
  - Nhật ký làm việc tuần 4: [worklog/LeHuy/Week_04.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/worklog/LeHuy/Week_04.md).
- **Tổng hợp kết quả kiểm thử:**
  - Báo cáo kết quả kiểm thử tuần 4: [tests/Week_04/results.md](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/tests/Week_04/results.md).

---

## 3. TÌNH TRẠNG HỆ THỐNG VÀ CHUẨN BỊ BÀN GIAO

- **Trạng thái hệ thống:** Hệ thống hoàn tất 100% mục tiêu đề tài, các luồng chính và ngoại lệ vận hành ổn định trên AWS.
- **Tài nguyên và chi phí:** Vận hành 100% Serverless, chi phí thực tế tối ưu (dưới $0.20) trong hạn mức AWS Academy Learner Lab.
- **Video demo dự án:** Video hoàn tất luồng thời gian thực, lưu tại: [demo/FoodDeliveryRealtimeDemo.mp4](https://github.com/henrynlh/FoodDeliveryRealtime/blob/main/demo/FoodDeliveryRealtimeDemo.mp4).

---

## 4. LỊCH SỬ COMMIT PHẢN ÁNH CÔNG VIỆC TUẦN 4

Danh sách toàn bộ commit của nhóm: [GitHub Commits](https://github.com/henrynlh/FoodDeliveryRealtime/commits/main).

| STT | Commit SHA | Tác giả | Thông điệp commit & Nội dung phản ánh |
|:---:|:---:|:---:|:---|
| 1 | [28ee3f9](https://github.com/henrynlh/FoodDeliveryRealtime/commit/28ee3f948bb8f2d5411733f240d235ea8e60ee57) | Nguyễn Lê Huy | Thêm kế hoạch phân công, kiểm thử và hoàn thiện đồ án tuần 4. |
| 2 | [ab209c6](https://github.com/henrynlh/FoodDeliveryRealtime/commit/ab209c6b35ea27113e33b85f9205c47b53184b78) | Nguyễn Lê Huy | Cập nhật giao diện khách hàng tuần 4. |
| 3 | [f2122ae](https://github.com/henrynlh/FoodDeliveryRealtime/commit/f2122ae560eb2fbc4ffecdae086aea43d682f6a1) | Nguyễn Lê Huy | Cập nhật giao diện tài xế tuần 4. |
| 4 | [f5c747b](https://github.com/henrynlh/FoodDeliveryRealtime/commit/f5c747b889ff4473b2d462a0cef9983d23daf2a8) | Nguyễn Lê Huy | Xử lý trạng thái kết thúc và khôi phục sau CONFLICT. |
| 5 | [db424c6](https://github.com/henrynlh/FoodDeliveryRealtime/commit/db424c697cade4561f1a8addec328905d45d6a5f) | Nguyễn Lê Huy | Bổ sung minh chứng kiểm thử giao diện và WebSocket. |
| 6 | [236a587](https://github.com/henrynlh/FoodDeliveryRealtime/commit/236a587078444d701bb10be3a7dc8cb9d3efacfd) | Nguyễn Lê Huy | Ghi nhật ký kiểm thử và đối chiếu log. |
| 7 | [3aa1831](https://github.com/henrynlh/FoodDeliveryRealtime/commit/3aa18317cf445bd197d66fccd2b22d8c53c245f8) | Trương Tấn Phát | Cấu trúc luồng công việc (cấu hình Step Functions ASL live tuần 4). |
| 8 | [caff1a7](https://github.com/henrynlh/FoodDeliveryRealtime/commit/caff1a71fa1490e5651d9f0128a035473d23f544) | Trương Tấn Phát | Các file để tạo các test kiểm lỗi (bộ script kiểm thử backend TV1). |
| 9 | [7588183](https://github.com/henrynlh/FoodDeliveryRealtime/commit/758818359b1764011910c8ce82fdc908f100bd9f) | Trương Tấn Phát | Các minh chứng cho TV1 (bộ 21 ảnh minh chứng và JSON kết quả). |
| 10 | [317a118](https://github.com/henrynlh/FoodDeliveryRealtime/commit/317a118141fd9d13ee3ffbea3db6563c9a17bbdb) | Trương Tấn Phát | Nội dung công việc tuần 4 (nhật ký làm việc TV1 tuần 4). |
| 11 | [5a5ef41](https://github.com/henrynlh/FoodDeliveryRealtime/commit/5a5ef41431b30e2a40b5d56a139ccfe66034d196) | Nguyễn Lê Huy | Bổ sung minh chứng tranh nhận đơn, đối chiếu timeout và che callback token. |
| 12 | [dee9ef4](https://github.com/henrynlh/FoodDeliveryRealtime/commit/dee9ef48aae530161f2a99794f61c27115dd3163) | Nguyễn Lê Huy | Ghi nhận kiểm thử bổ sung backend TV1. |
| 13 | [c9e305e](https://github.com/henrynlh/FoodDeliveryRealtime/commit/c9e305e836aa472d0931cfc6043d7c53b9fe9144) | Nguyễn Lê Huy | Tổng hợp bàn giao backend và kết quả đối chiếu. |
| 14 | [644f182](https://github.com/henrynlh/FoodDeliveryRealtime/commit/644f182134f45cb1ffe910d8087d76a2ae62d29d) | Nguyễn Lê Huy | Bổ sung minh chứng ngân sách Learner Lab. |
| 15 | [182d406](https://github.com/henrynlh/FoodDeliveryRealtime/commit/182d40602f0bb96904b0969a5e92e1aad82b910f) | Nguyễn Lê Huy | Cập nhật ghi nhận ngân sách lab. |
| 16 | [6941334](https://github.com/henrynlh/FoodDeliveryRealtime/commit/6941334bf6d0d2b4a65cdc251c742f01fbbce57e) | Nguyễn Lê Huy | Bổ sung minh chứng kiểm kê tài nguyên. |
| 17 | [678c69e](https://github.com/henrynlh/FoodDeliveryRealtime/commit/678c69e4e740f63deeb3c60bcc3a08b3a4d410d8) | Nguyễn Lê Huy | Ghi nhận tài nguyên và phương án bàn giao. |
| 18 | [8427e82](https://github.com/henrynlh/FoodDeliveryRealtime/commit/8427e8275d81fe6715985588149ff8e3708fe25c) | Nguyễn Lê Huy | Tổng hợp kết quả kiểm thử và giới hạn đối chiếu. |
| 19 | [9d496f0](https://github.com/henrynlh/FoodDeliveryRealtime/commit/9d496f081741b78f910ba540aee2d51b25f4a4c3) | Nguyễn Lê Huy | Bổ sung minh chứng giao diện khi workflow FAILED. |
| 20 | [b62a872](https://github.com/henrynlh/FoodDeliveryRealtime/commit/b62a872d290ddc307a902f9424f8766792efdc52) | Nguyễn Lê Huy | Ghi nhật ký kiểm thử workflow FAILED. |
| 21 | [f803edf](https://github.com/henrynlh/FoodDeliveryRealtime/commit/f803edffa6aa5e0a98189635019e0e703f931f4f) | Nguyễn Lê Huy | Hoàn thiện hồ sơ và kết quả kiểm thử tuần 4. |
| 22 | [740a7b3](https://github.com/henrynlh/FoodDeliveryRealtime/commit/740a7b380f610dac318a63bd93ce4aba467ac397) | Trương Tấn Phát | Thêm video demo dự án (demo/FoodDeliveryRealtimeDemo.mp4 qua Git LFS). |
