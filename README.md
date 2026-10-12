Ứng dụng Giao đồ ăn: Theo dõi trạng thái đơn hàng theo thời gian thực

Thông tin sinh viên & Đồ án

Môn học: Điện toán đám mây (Cloud Computing) - Đợt 1 (2026 - 2027)

Giảng viên hướng dẫn: ThS. Huỳnh Xuân Phụng

Nhóm đề tài: Domain Apps

Nhóm thực hiện:

Nguyễn Văn A - MSSV: 24110xxx

Trần Văn B - MSSV: 24110xxx

AWS Region: us-east-1 (N. Virginia)

Kiến trúc hệ thống Serverless & Luồng dữ liệu (5 Thành phần chính)

Thành phần 1 (State Orchestration): AWS Step Functions điều phối vòng đời đơn hàng theo luồng trạng thái (Đặt hàng → Nhà hàng nhận → Đang giao → Hoàn tất).

Thành phần 2 (Real-time Communication): Amazon API Gateway WebSocket duy trì kết nối hai chiều liên tục với Web client của khách hàng và shipper.

Thành phần 3 (Compute & Business Logic): AWS Lambda (sử dụng IAM LabRole) xử lý logic kết nối WebSocket ($connect, $disconnect), trigger State Machine và đẩy thông báo.

Thành phần 4 (Data Persistence): Amazon DynamoDB lưu trữ chi tiết đơn hàng (OrdersTable) và quản lý danh sách connection ID active (ConnectionsTable).

Thành phần 5 (Notification Service): Amazon SNS gửi cảnh báo / thông báo trạng thái đơn hàng tới khách hàng và đối tác giao hàng.