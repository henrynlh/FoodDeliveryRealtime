# BÀN GIAO BACKEND TUẦN 4

- Dự án: FoodDeliveryRealtime.
- Người phụ trách backend: Trương Tấn Phát — TV1 — 24110298.
- Người tổng hợp và kiểm thử bổ sung: Nguyễn Lê Huy — TV2 — 24110221.
- Ngày tổng hợp: 01/11/2026.
- Region: us-east-1.
- Execution Role: LabRole.

## 1. Môi trường và phạm vi bàn giao

| Môi trường | AWS Account ID | Nội dung đã kiểm tra |
|---|---|---|
| TV1 | 053151184394 | Workflow, lỗi commit có kiểm soát, luồng thành công, timeout chờ nhận đơn, submit trễ, gửi lặp và SNS. |
| TV2 | 165662523632 | Giao diện và WebSocket, ba ca timeout, phục hồi kết nối, phục hồi sau CONFLICT, truy vết log và kiểm thử tranh nhận đơn bổ sung. |

Các kết quả thuộc hai môi trường độc lập. Không dùng ARN, endpoint hoặc thông tin xác thực của môi trường này cho môi trường còn lại.

Môi trường được chọn để quay demo chung là tài khoản TV2. Cần chạy thử kịch bản trên môi trường này trước khi quay. Minh chứng SNS và lỗi commit trên tài khoản TV1 không thay thế việc xác nhận các chức năng đó trên môi trường demo.

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

Dispatcher và Broadcast do TV2 phụ trách, kết nối giao diện với các thành phần backend.

## 3. Mã nguồn và phiên bản tham chiếu

| Nội dung | Đường dẫn | Commit tham chiếu |
|---|---|---|
| Workflow xuất từ môi trường TV1 | config/TanPhat/Week_04/w4-workflow-live.asl.json | 3aa1831 |
| Script kiểm thử tuần 4 | tests/Week_04/ | caff1a7 |
| Minh chứng TV1 ban đầu | evidence/TanPhat/Week_04/ | 7588183 |
| Worklog TV1 | worklog/TanPhat/Week_04.md | 317a118 |
| Lambda backend kế thừa | code/TanPhat/Week_03/ | Tham chiếu tại phiên bản repo 317a118. |

Không có thư mục mã Lambda mới của TV1 trong tuần 4 tại phiên bản repo đã rà soát. Mã nguồn backend được dẫn chiếu từ tuần 3.

Các commit trên xác định nội dung trong repository. Chưa có bản đối chiếu CodeSha256 hoặc Lambda version để khẳng định toàn bộ mã Lambda đang triển khai trên hai tài khoản giống hệt nội dung repository.

File workflow của TV1 chứa ARN tài khoản 053151184394. Không dán nguyên file này để triển khai trên tài khoản TV2 nếu chưa điều chỉnh các ARN và kiểm tra cấu hình liên quan.

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
| Luồng thành công trên TV1 | Đơn COMPLETED, version 4. Ba task đã hoàn thành. |
| Lỗi commit có kiểm soát trên TV1 | Sai actor giữ claim bị từ chối. Orders giữ PLACED, version 1, lưu workflowStatus FAILED. Task không bị chuyển DONE. |
| Timeout chờ nhận đơn trên TV1 | Orders giữ PLACED, version 1, lưu TIMED_OUT và thời gian kết thúc. |
| Submit sau timeout trên TV1 | TASK_EXPIRED, trạng thái nghiệp vụ và version không đổi. |
| Gửi lặp trên TV1 | Submit trả ALREADY_DONE. Commit lặp trả duplicate true và SKIPPED_DUPLICATE. |
| SNS trên TV1 | Có kết quả PUBLISHED và minh chứng email thông báo. |
| Tranh nhận đơn bổ sung trên TV2 | D001 bị CONFLICT. D002 nhận đơn thành công. Orders ACCEPTED, version 2, driverId D002. Task ACCEPTED DONE, committedVersion 2. |
| Timeout chờ bắt đầu giao trên TV2 | Orders giữ ACCEPTED, version 2, lưu TIMED_OUT. Task ACCEPTED DONE, DELIVERING chưa hoàn thành. |
| Timeout chờ hoàn tất trên TV2 | Orders giữ DELIVERING, version 3, lưu TIMED_OUT. ACCEPTED và DELIVERING DONE; COMPLETED chưa hoàn thành. |

Kiểm thử lỗi commit chỉ xác nhận điều kiện actor giữ claim và nhánh Catch lưu lỗi. Không suy rộng thành đã kiểm thử mọi loại lỗi giao dịch DynamoDB.

Ca tranh nhận đơn đạt trong lần thử đã ghi nhận. Không xem đây là kết quả kiểm thử tải lớn.

Task còn READY sau timeout không chứng minh callback còn hiệu lực. Cần kiểm tra thời hạn, execution và phản hồi yêu cầu đến trễ.

## 6. Mã đơn kiểm thử bổ sung trên TV2

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
- Đơn đã commit nhưng thông báo lỗi: kiểm tra kết quả SNS và Broadcast. Không gửi lại commit một cách mù quáng.
- Nhật ký không tìm thấy: kiểm tra tài khoản, region, khoảng thời gian, múi giờ và mã yêu cầu.
- Khi chụp dữ liệu task: chỉ hiển thị các thuộc tính cần đối chiếu, không hiển thị callback token.

## 8. Tài liệu và minh chứng liên quan

- [Kế hoạch tuần 4](../../TaskAssignments/Week_04.md).
- [Worklog TV1](../../worklog/TanPhat/Week_04.md).
- [Worklog TV2](../../worklog/LeHuy/Week_04.md).
- [Workflow TV1](../../config/TanPhat/Week_04/w4-workflow-live.asl.json).
- [Script kiểm thử](../../tests/Week_04/).
- [Minh chứng backend](../../evidence/TanPhat/Week_04/).
- [Minh chứng giao diện và WebSocket](../../evidence/LeHuy/Week_04/).

## 9. Nội dung còn cần chốt

- Đối chiếu cấu hình và mã triển khai trên môi trường demo.
- Chạy thử phần backend cần trình diễn trên tài khoản TV2.
- Tổng hợp kết quả vào tests/Week_04/results.md.
- Ghi nhận budget, thời điểm kiểm tra và danh sách tài nguyên cần giữ.
- Mỗi thành viên bổ sung giờ làm thực tế vào worklog.
- Hoàn thiện báo cáo và video demo chung không quá 10 phút.

Chưa kết luận toàn bộ hồ sơ tuần 4 hoàn thành khi các mục trên chưa được đối chiếu.