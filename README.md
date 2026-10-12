# Ứng dụng Giao đồ ăn: Theo dõi trạng thái đơn hàng theo thời gian thực

## Thông tin sinh viên & Đồ án

* **Môn học:** Điện toán đám mây (Cloud Computing)
* **Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng
* **Nhóm đề tài:** Domain Apps
* **Nhóm thực hiện:**
  * Nguyễn Lê Huy - MSSV: 24110221
  * Trương Tấn Phát - MSSV: 24110298
* **AWS Region:** `us-east-1` (N. Virginia)

## Các thành phần chính trong kiến trúc:

1. **Static Web Hosting (Amazon S3):** Lưu trữ mã nguồn giao diện Web Frontend phục vụ khách hàng đặt món và nhân viên giao hàng cập nhật trạng thái.
2. **Kênh truyền hai chiều (API Gateway WebSocket):** Tiếp nhận yêu cầu từ Web Client và đẩy dữ liệu trạng thái đơn hàng thời gian thực (`@connections`) xuống giao diện.
3. **Lambda Xử lý yêu cầu (Xác thực & Kiểm tra):** Định tuyến sự kiện kết nối/ngắt kết nối, xác thực yêu cầu, kiểm tra dữ liệu từ DynamoDB và khởi tạo hoặc gửi callback (`SendTaskSuccess`) tới Step Functions.
4. **State Machine Orchestration (AWS Step Functions Standard):** Điều phối luồng trạng thái đơn hàng (`Đặt hàng` → `Nhận đơn` → `Đang giao` → `Hoàn tất`) với cơ chế Task Token / Chờ callback.
5. **Lambda Workflow (Đăng ký chờ & Cập nhật):** Được kích hoạt bởi Task trong Step Functions để ghi nhận trạng thái chờ, lưu task token vào DynamoDB và gọi kích hoạt thông báo.
6. **Lưu trữ dữ liệu (Amazon DynamoDB):** Quản lý tập trung các bảng:
   * `Orders`: Thông tin chi tiết đơn hàng và trạng thái hiện tại.
   * `Connections`: Danh sách `connectionId` của WebSocket client đang hoạt động.
   * `WorkflowTasks`: Lưu trữ task token phục vụ cơ chế resume workflow callback.
7. **Lambda Thông báo Realtime & SNS:** Đọc danh sách kết nối từ DynamoDB để gửi dữ liệu qua API Gateway WebSocket Management API (`@connections`), đồng thời kích hoạt gửi email/SMS thông báo qua **Amazon SNS Standard**.

## Kế hoạch 4 tuần

### Tuần 1: Tìm hiểu và dựng nền tảng
* Thiết kế kiến trúc, mô hình dữ liệu, khởi tạo tài nguyên có gắn tag (`Project`, `Owner`).
* Kiểm thử nền tảng và lập nhật ký công việc (worklog) cá nhân.

### Tuần 2: Triển khai chức năng
* Xây dựng chức năng tạo và đọc đơn hàng (DynamoDB, Lambda).
* Khởi chạy workflow trên AWS Step Functions.
* Xử lý và lưu trữ callback (Task Token / WebSocket Connection).
* Cập nhật trạng thái và kiểm thử độc lập từng thành phần.

### Tuần 3: Tích hợp và bảo mật
* Xây dựng và liên kết luồng đơn hàng thống nhất (E2E flow).
* Kiểm tra phân quyền theo chuẩn `LabRole`, thiết lập giám sát bằng Amazon CloudWatch.
* Tự động hóa cấu hình và triển khai (IaC/Scripts) nếu phù hợp.

### Tuần 4: Kiểm thử và hoàn thiện
* Kiểm thử toàn bộ hệ thống từ giao diện Web đến dịch vụ AWS.
* Tổng hợp và tối ưu chi phí, dọn dẹp các tài nguyên không cần thiết.
* Hoàn thiện báo cáo đồ án và chuẩn bị video demo không quá 10 phút.
