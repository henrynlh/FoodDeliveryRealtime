# TÀI LIỆU TRIỂN KHAI VÀ VẬN HÀNH – TUẦN 3 (DEPLOYMENT GUIDE)

- **Hệ thống:** FoodDeliveryRealtime
- **Vùng triển khai:** AWS `us-east-1` (N. Virginia)
- **Tài khoản tích hợp:** Tài khoản nhóm (Nguyễn Lê Huy / Trương Tấn Phát)
- **Execution Role:** `LabRole` (mặc định của AWS Academy / Learner Lab)

---

## 1. Cấu hình bảng DynamoDB

| Tên bảng (Table Name) | Partition Key | Sort Key | Biến môi trường tương ứng | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `fooddelivery-orders` | `orderId` (String) | *(None)* | `ORDERS_TABLE` | Lưu trữ thông tin đơn hàng, trạng thái, version và tài xế phụ trách |
| `fooddelivery-workflow-tasks` | `orderId` (String) | `step` (String) | `WORKFLOW_TASKS_TABLE` | Lưu Task Token callback, trạng thái bước chờ (`READY`, `CLAIMED`, `DONE`) |
| `fooddelivery-connections` | `connectionId` (String) | *(None)* | `CONNECTIONS_TABLE` | Quản lý các kết nối WebSocket client hiện tại |

---

## 2. Thông số kỹ thuật các Lambda Functions

| Tên Lambda | Runtime | Handler | Memory / Timeout | Execution Role | Biến môi trường chính |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `fooddelivery-prepare-task` | Python 3.12 | `lambda_function.lambda_handler` | 128 MB / 20s | `LabRole` | `WORKFLOW_TASKS_TABLE`, `ORDERS_TABLE` |
| `fooddelivery-submit-transition` | Python 3.12 | `lambda_function.lambda_handler` | 128 MB / 20s | `LabRole` | `WORKFLOW_TASKS_TABLE`, `ORDERS_TABLE` |
| `fooddelivery-commit-transition` | Python 3.12 | `lambda_function.lambda_handler` | 128 MB / 20s | `LabRole` | `ORDERS_TABLE`, `WORKFLOW_TASKS_TABLE`, `SNS_TOPIC_ARN` |
| `fooddelivery-broadcast` | Python 3.12 | `lambda_function.lambda_handler` | 128 MB / 30s | `LabRole` | `WEBSOCKET_API_ENDPOINT`, `CONNECTIONS_TABLE`, `ORDERS_TABLE` |
| `fooddelivery-ws-dispatcher` | Python 3.12 | `lambda_function.lambda_handler` | 128 MB / 30s | `LabRole` | `STATE_MACHINE_ARN`, `SUBMIT_LAMBDA_ARN`, `ORDERS_TABLE`, `CONNECTIONS_TABLE` |

---

## 3. Thứ tự triển khai trên AWS (Deployment Sequence)

Để đảm bảo tính toàn vẹn hệ thống và không làm gián đoạn tích hợp, thứ tự triển khai như sau:

1. **Bước 1 — Cập nhật mã nguồn 3 Lambda Backend của TV1:**
   - Deploy code [prepare-task/lambda_function.py](../../code/TanPhat/Week_03/prepare-task/lambda_function.py) lên `fooddelivery-prepare-task`.
   - Deploy code [submit-transition/lambda_function.py](../../code/TanPhat/Week_03/submit-transition/lambda_function.py) lên `fooddelivery-submit-transition`.
   - Deploy code [commit-transition/lambda_function.py](../../code/TanPhat/Week_03/commit-transition/lambda_function.py) lên `fooddelivery-commit-transition`.
2. **Bước 2 — Cập nhật State Machine Step Functions:**
   - Mở Step Functions Console $\rightarrow$ State machine `fooddelivery-order-workflow` $\rightarrow$ Edit Code $\rightarrow$ Dán nội dung từ [config/TanPhat/Week_03/order_workflow.asl.json](../../config/TanPhat/Week_03/order_workflow.asl.json) $\rightarrow$ Lưu và Verify.
   - *Lưu ý:* Luồng ASL này tích hợp sẵn 3 bước Broadcast của TV2 (`BroadcastAccepted`, `BroadcastDelivering`, `BroadcastCompleted`).
3. **Bước 3 — Kiểm tra cấu hình Amazon SNS:**
   - Topic `fooddelivery-order-events` đã có Subscription Email xác nhận (`Confirmed`).
   - Gắn biến `SNS_TOPIC_ARN` vào Lambda `fooddelivery-commit-transition`.
4. **Bước 4 — Chạy Smoke Test:**
   - Mở giao diện `customer.html` tạo đơn smoke test và cho `driver.html` nhận đơn để xác nhận toàn bộ chuỗi thông suốt.

---

## 4. Hướng dẫn vận hành & Kiểm thử

1. **Giao diện Web:**
   - Mở [customer.html](../../code/LeHuy/Week_03/frontend/customer.html) cho khách hàng (Phiên C001).
   - Mở [driver.html](../../code/LeHuy/Week_03/frontend/driver.html) cho tài xế (Phiên D001 / D002).
   - WebSocket URL: `wss://lob1j5l21i.execute-api.us-east-1.amazonaws.com/dev/`.
2. **Kiểm thử tự động bằng Script:**
   - Test gửi lặp (TC02): `py tests/Week_03/ws_request.py --request tests/Week_03/request.json --out evidence/TanPhat/Week_03/response.json`.
   - Test tranh chấp tài xế (TC12): `py tests/Week_03/race_accept.py`.
3. **Tra cứu Log CloudWatch:**
   - Lọc theo chuỗi chính xác mã đơn `"ORD-..."` hoặc `requestId` trên Log Groups `/aws/lambda/fooddelivery-submit-transition` và `/aws/lambda/fooddelivery-commit-transition`.

---

## 5. Giới hạn môi trường AWS Learner Lab

- Execution Role cố định là `LabRole`, không có quyền tạo/sửa IAM Policy.
- Log retention mặc định (Never Expire).
- Token phiên demo dùng độc lập cho mục đích kiểm thử học phần, không lưu trữ token phiên hay `taskToken` vào Git repository.
