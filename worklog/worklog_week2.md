# BÁO CÁO CÔNG VIỆC TUẦN 2

## 1. Thông tin chung

* **Đề tài:** Ứng dụng giao đồ ăn – Theo dõi trạng thái đơn hàng theo thời gian thực
* **Tên dự án:** FoodDeliveryRealtime

## 2. Phân công nhiệm vụ & Thời gian thực hiện

| STT | Họ và tên | MSSV | Nhiệm vụ đảm nhiệm | Giờ làm (h) |
| :---: | :--- | :---: | :--- | :---: |
| 1 | **Trương Tấn Phát** | 24110298 | Thiết kế State Machine nghiệp vụ, cơ chế Callback, viết 3 Lambda (Prepare, Submit, Commit), tích hợp SNS và kiểm thử backend (TC05 - TC12) | 7-8h |
| 2 | **Nguyễn Lê Huy** | 24110221 | Triển khai lại backend, xây dựng giao diện (customer.html, driver.html), tích hợp WebSocket broadcast và kiểm thử phân quyền, kết nối lại | 7-8h |

**Thời gian thảo luận chung:** 3-4h

## 3. Chi tiết tiến độ thực hiện

### 3.1. Trương Tấn Phát
* Thiết kế và triển khai workflow nghiệp vụ `fooddelivery-order-workflow` trên AWS Step Functions (Standard Workflow, cơ chế `waitForTaskToken`, xử lý timeout và error handling).
* Xây dựng và cấu hình 3 Lambda Functions nghiệp vụ backend:
  * `fooddelivery-prepare-task`: Khởi tạo bước chờ, lưu `taskToken` vào bảng `fooddelivery-workflow-tasks`.
  * `fooddelivery-submit-transition`: Tiếp nhận yêu cầu chuyển trạng thái, claim bước chờ (chống tranh chấp) và gửi callback `send_task_success`.
  * `fooddelivery-commit-transition`: Xác thực nghiệp vụ, cập nhật trạng thái đơn hàng, tăng version trong bảng `fooddelivery-orders` và gán `driverId`.
* Cấu hình Amazon SNS (`fooddelivery-order-events`) và tích hợp tự động phát thông báo đơn hàng sau khi commit thành công.
* Thực hiện bộ kiểm thử backend độc lập: TC05 (toàn luồng hợp lệ), TC06 (chống gửi lặp), TC07 (sai trạng thái/version cũ), TC08 (2 tài xế tranh chấp nhận đơn), TC09 (timeout chờ callback) và TC12 (SNS tự động).

### 3.2. Nguyễn Lê Huy
* Triển khai đồng bộ phần backend trên môi trường cá nhân để phục vụ tích hợp toàn diện.
* Xây dựng giao diện ứng dụng web phía người dùng: giao diện khách hàng (`customer.html`) và giao diện tài xế (`driver.html`).
* Tích hợp WebSocket API và Lambda broadcast cập nhật trạng thái đơn hàng thời gian thực.
* Thực hiện kiểm thử tích hợp hệ thống (End-to-End):
  * Kiểm thử luồng tạo đơn và cơ chế chống gửi lặp tạo đơn (`createOrder`).
  * Kiểm thử giao diện và xử lý tranh chấp khi 2 tài xế cùng bấm nhận 1 đơn hàng.
  * Kiểm thử ma trận phân quyền khách hàng và tài xế (chặn đọc/theo dõi đơn trái quyền với mã `FORBIDDEN`).
  * Kiểm thử kịch bản khách hàng ngắt kết nối mạng, kết nối lại (`reconnect`) và nhận bản tin cập nhật (`ORDER_UPDATED`).
