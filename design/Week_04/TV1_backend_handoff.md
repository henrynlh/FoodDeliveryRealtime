# BÀN GIAO BACKEND TUẦN 4

- Dự án: FoodDeliveryRealtime.
- Người phụ trách backend: Trương Tấn Phát — MSSV 24110298.
- Người tổng hợp và kiểm thử bổ sung: Nguyễn Lê Huy — MSSV 24110221.
- Ngày tổng hợp: 01/11/2026.
- Region: us-east-1.
- Execution Role: LabRole.

## 1. Môi trường và phạm vi bàn giao

| Môi trường | AWS Account ID | Nội dung đã kiểm tra |
|---|---|---|
| Phát | 053151184394 | Workflow, lỗi commit có kiểm soát, luồng thành công, timeout chờ nhận đơn, submit trễ, gửi lặp và SNS. |
| Huy | 165662523632 | Giao diện và WebSocket, ba ca timeout, phục hồi kết nối, phục hồi sau CONFLICT, truy vết log và kiểm thử tranh nhận đơn bổ sung. |

Nhóm sử dụng hai môi trường độc lập, mỗi môi trường có ARN, endpoint và cấu hình xác thực riêng.

Nhóm chọn tài khoản của Huy để quay demo chung. Kết quả backend trên tài khoản của Phát và kết quả tích hợp trên tài khoản của Huy được ghi riêng trong tài liệu kiểm thử.

## 2. Thành phần backend

| Thành phần | Tên tài nguyên | Chức năng |
|---|---|---|
| Step Functions | fooddelivery-order-workflow | Điều phối các bước nhận đơn, bắt đầu giao và hoàn tất. |
| Lambda Prepare | fooddelivery-prepare-task | Chuẩn bị bước chờ và lưu callback token. |
| Lambda Submit | fooddelivery-submit-transition | Kiểm tra yêu cầu, giữ quyền xử lý task và gửi callback. |
| Lambda Commit | fooddelivery-commit-transition | Cập nhật Orders và WorkflowTasks trong cùng giao dịch. |
| DynamoDB Orders | fooddelivery-orders | Lưu trạng thái, phiên bản và tài xế của đơn. |
| DynamoDB WorkflowTasks | fooddelivery-workflow-tasks | Lưu trạng thái xử lý từng bước. Khóa gồm orderId và step. |
| SNS | fooddelivery-order-events | Thông báo tại các mốc ACCEPTED và COMPLETED theo cấu hình. |

Dispatcher và Broadcast do Huy phụ trách, kết nối giao diện với các thành phần backend.

## 3. Mã nguồn và phiên bản tham chiếu

| Nội dung | Đường dẫn | Commit tham chiếu |
|---|---|---|
| Workflow xuất từ môi trường của Phát | config/TanPhat/Week_04/w4-workflow-live.asl.json | 3aa1831 |
| Script kiểm thử tuần 4 | tests/Week_04/ | caff1a7 |
| Minh chứng của Phát ban đầu | evidence/TanPhat/Week_04/ | 7588183 |
| Worklog của Phát | worklog/TanPhat/Week_04.md | 317a118 |
| Lambda backend kế thừa | code/TanPhat/Week_03/ | Tham chiếu tại phiên bản repo 317a118. |

Phần Lambda backend của Phát kế thừa mã nguồn tuần 3. Tuần 4 tập trung cập nhật workflow và bổ sung các script kiểm thử.

Các commit trên xác định nội dung trong repository. Chưa có bản đối chiếu CodeSha256 hoặc Lambda version để khẳng định toàn bộ mã Lambda đang triển khai trên hai tài khoản giống hệt nội dung repository.

Tệp workflow của Phát chứa ARN thuộc tài khoản 053151184394; khi sử dụng ở tài khoản khác, các ARN và cấu hình liên quan phải trỏ đúng môi trường triển khai.

## 4. Cấu hình cần đối chiếu

- ORDERS_TABLE: fooddelivery-orders.
- WORKFLOW_TASKS_TABLE: fooddelivery-workflow-tasks.
- SNS_TOPIC_ARN: ARN topic thuộc đúng tài khoản triển khai.
- Ba bước Prepare dùng cơ chế waitForTaskToken, TimeoutSeconds bằng 300.
- Các bước Commit có Catch chuyển sang HandleWorkflowError.
- Nhánh timeout đi qua HandleTimeout.
- Hai nhánh lỗi chuyển đến PersistWorkflowFailure để lưu kết quả vào Orders, sau đó kết thúc tại WorkflowFailed.
- LabRole cần quyền phù hợp với DynamoDB, Step Functions, Lambda, CloudWatch và SNS theo thao tác thực tế.

Không lưu access key, secret key, session token, token phiên hoặc callback token trong tài liệu.

## 5. Kết quả kiểm thử đã ghi nhận

| Nội dung | Kết quả |
|---|---|
| Luồng thành công trên môi trường của Phát | Đơn COMPLETED, version 4. Ba task đã hoàn thành. |
| Lỗi commit có kiểm soát trên môi trường của Phát | Sai actor giữ claim bị từ chối. Orders giữ PLACED, version 1, lưu workflowStatus FAILED. Task không bị chuyển DONE. |
| Timeout chờ nhận đơn trên môi trường của Phát | Orders giữ PLACED, version 1, lưu TIMED_OUT và thời gian kết thúc. |
| Submit sau timeout trên môi trường của Phát | TASK_EXPIRED, trạng thái nghiệp vụ và version không đổi. |
| Gửi lặp trên môi trường của Phát | Submit trả ALREADY_DONE. Commit lặp trả duplicate true và SKIPPED_DUPLICATE. |
| SNS trên môi trường của Phát | Có kết quả PUBLISHED và minh chứng email thông báo. |
| Tranh nhận đơn bổ sung trên môi trường của Huy | D001 bị CONFLICT. D002 nhận đơn thành công. Orders ACCEPTED, version 2, driverId D002. Task ACCEPTED DONE, committedVersion 2. |
| Timeout chờ bắt đầu giao trên môi trường của Huy | Orders giữ ACCEPTED, version 2, lưu TIMED_OUT. Task ACCEPTED DONE, DELIVERING chưa hoàn thành. |
| Timeout chờ hoàn tất trên môi trường của Huy | Orders giữ DELIVERING, version 3, lưu TIMED_OUT. ACCEPTED và DELIVERING DONE; COMPLETED chưa hoàn thành. |

Kiểm thử lỗi commit chỉ xác nhận điều kiện actor giữ claim và nhánh Catch lưu lỗi. Không suy rộng thành đã kiểm thử mọi loại lỗi giao dịch DynamoDB.

Ca tranh nhận đơn đạt trong lần thử đã ghi nhận. Không xem đây là kết quả kiểm thử tải lớn.

Task còn READY sau timeout không chứng minh callback còn hiệu lực. Cần kiểm tra thời hạn, execution và phản hồi yêu cầu đến trễ.

## 6. Mã đơn kiểm thử bổ sung trên môi trường của Huy

| Nội dung | Mã đơn |
|---|---|
| Tranh nhận đơn | ORD-87610c608da45f2e46989b4a |
| Timeout chờ bắt đầu giao | ORD-3e832b119b6cc9ebe3cecc86 |
| Timeout chờ hoàn tất | ORD-be0dec6579d25293f355a7de |

Ca tranh nhận đơn được thực hiện ngày 01/11/2026 theo giờ Việt Nam.

Hai đơn timeout được kiểm thử ngày 30/10/2026. Ngày 01/11/2026 thực hiện đối chiếu bổ sung dữ liệu Orders và WorkflowTasks.

## 7. Kiểm tra và xử lý sự cố

- QUEUED chỉ xác nhận đã tiếp nhận yêu cầu. Kiểm tra Orders và WorkflowTasks để xác nhận commit.
- CONFLICT: đọc lại đơn và kiểm tra trạng thái, version, actor giữ claim trước khi thao tác tiếp.
- TASK_EXPIRED hoặc CALLBACK_INVALID: kiểm tra execution. Không tiếp tục dùng task đã hết hiệu lực.
- Commit lỗi: xem CloudWatch của Commit, lịch sử execution và kết quả PersistWorkflowFailure.
- Đơn đã commit nhưng gửi thông báo thất bại: kiểm tra kết quả SNS và Broadcast, đối chiếu dữ liệu đơn trước khi quyết định gửi lại yêu cầu.
- Nhật ký không tìm thấy: kiểm tra tài khoản, region, khoảng thời gian, múi giờ và mã yêu cầu.
- Khi chụp dữ liệu task: chỉ hiển thị các thuộc tính cần đối chiếu, không hiển thị callback token.

## 8. Tài liệu và minh chứng liên quan

- [Kế hoạch tuần 4](../../TaskAssignments/Week_04.md).
- [Worklog của Phát](../../worklog/TanPhat/Week_04.md).
- [Worklog của Huy](../../worklog/LeHuy/Week_04.md).
- [Workflow của Phát](../../config/TanPhat/Week_04/w4-workflow-live.asl.json).
- [Script kiểm thử](../../tests/Week_04/).
- [Minh chứng backend](../../evidence/TanPhat/Week_04/).
- [Minh chứng giao diện và WebSocket](../../evidence/LeHuy/Week_04/).
