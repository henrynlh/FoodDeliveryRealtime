# Nhật ký làm việc tuần 2

- Người thực hiện: Trương Tấn Phát – 24110298.
- Vai trò: Thành viên 1 (TV1).
- Người phối hợp: Nguyễn Lê Huy – 24110221, Thành viên 2 (TV2).
- Nội dung phụ trách: workflow nghiệp vụ, Lambda Prepare, Submit, Commit và SNS.
- Giai đoạn thực hiện đã có minh chứng: 14/10/2026 đến 16/10/2026. Các lần thử bổ sung ghi theo ngày chạy thật.
- Tổng thời gian thực hiện: bổ sung từ nhật ký giờ thực tế trước khi nộp.
- Region: `us-east-1`.

## Phân công thực hiện và triển khai tích hợp

- Phát xây dựng và triển khai phần backend tuần 2 trên tài khoản AWS `053151184394`.
- Huy triển khai lại phần backend trong môi trường của mình để tích hợp với customer.html, driver.html và kiểm thử.
- Minh chứng phần Phát triển khai được lưu tại `evidence/TanPhat/Week_02/`.
- Minh chứng Huy triển khai lại và kiểm thử được lưu tại `evidence/LeHuy/Week_02/`.
- Các ảnh của Huy được dẫn làm minh chứng tích hợp của nhóm, ghi rõ người thực hiện.
- Ảnh bổ sung của Phát dùng tên đã thống nhất trong bản hướng dẫn đi kèm. Các liên kết này có thể chưa có tệp cho đến khi kiểm thử xong.

## Kiểm tra Invoke và cơ chế callback

- State machine nền tảng: `MyStateMachine`.
- Execution role: `LabRole`.
- Execution Invoke `b421abb1-3de9-42b5-8469-d213aa7f16c5` kết thúc Succeeded.
- Execution trong ảnh CheckCallback `ce002a18-99b3-40ef-80eb-17aaa1838703` kết thúc Succeeded.
- Với workflow nghiệp vụ, bước Prepare đăng ký taskToken và chờ callback. Khi yêu cầu chuyển trạng thái hợp lệ được tiếp nhận, workflow tiếp tục sang bước Commit.
- Minh chứng bổ sung cần xác nhận: định nghĩa bước Task có waitForTaskToken và lịch sử bước chờ kết thúc trước khi Commit bắt đầu.

### Minh chứng

- [Invoke Lambda thành công](../../evidence/TanPhat/Week_02/E-TV1-01_CheckInvoke.png)
- [Execution kiểm tra callback](../../evidence/TanPhat/Week_02/E-TV1-02_CheckCallback.png)
- [Định nghĩa callback waitForTaskToken](../../evidence/TanPhat/Week_02/E-TV1-03_Callback_Definition.png)
- [Lịch sử callback và commit](../../evidence/TanPhat/Week_02/E-TV1-04_Callback_History.png)

## Thiết kế workflow nghiệp vụ

- State machine: `fooddelivery-order-workflow`.
- ARN môi trường Phát: `arn:aws:states:us-east-1:053151184394:stateMachine:fooddelivery-order-workflow`.
- Loại: Standard. Execution role: LabRole.
- Luồng trạng thái: `PLACED → ACCEPTED → DELIVERING → COMPLETED`.
- Các bước chờ: PrepareAcceptedTask, PrepareDeliveringTask và PrepareCompletedTask.
- Các bước ghi dữ liệu: CommitAcceptedTransition, CommitDeliveringTransition và CommitCompletedTransition.
- Hoàn tất tại OrderCompletedSucceed.
- Xử lý timeout qua HandleTimeout. Xử lý lỗi khác qua HandleWorkflowError. Luồng lỗi dẫn tới WorkflowFailed.
- Bản cấu hình đã chụp có giới hạn chờ 300 giây.
- Workflow được kiểm tra ở trạng thái chờ trước khi có callback và tiếp tục sau khi callback hợp lệ.

### Minh chứng

- [Định nghĩa và sơ đồ workflow](../../evidence/TanPhat/Week_02/E-TV1-05_Workflow_Config.png)
- [Thông tin và tags workflow](../../evidence/TanPhat/Week_02/E-TV1-06_Workflow_Tags.png)

## Lambda fooddelivery-prepare-task – đăng ký bước chờ

- ARN: `arn:aws:lambda:us-east-1:053151184394:function:fooddelivery-prepare-task`.
- Tệp mã nguồn trên Console: lambda_function.py.
- Role: LabRole. Memory: 128 MB. Timeout: 20 giây.
- Biến môi trường: WORKFLOW_TASKS_TABLE = fooddelivery-workflow-tasks.
- Đầu vào gồm orderId, step và taskToken.
- Ghi dữ liệu bước chờ gồm orderId, step, taskToken, taskState, createdAt và expiresAt.
- Trạng thái khởi tạo: READY.
- Mã nguồn hiển thị expiresAt = now + 1800. Đây là thời điểm hết hạn trong dữ liệu, không thay thế timeout 300 giây của workflow.
- Lambda lưu dữ liệu và trả WAITING_CALLBACK, không tự gửi callback ngay tại bước chuẩn bị.
- Bản ghi đã có minh chứng: ORD-TEST-001, step ACCEPTED, taskState READY.

### Minh chứng

- [Mã nguồn Prepare](../../evidence/TanPhat/Week_02/E-TV1-07_Prepare_Code.png)
- [Cấu hình Prepare](../../evidence/TanPhat/Week_02/E-TV1-08_Prepare_Config.png)
- [Biến môi trường Prepare](../../evidence/TanPhat/Week_02/E-TV1-09_Prepare_Environment.png)
- [Role Prepare](../../evidence/TanPhat/Week_02/E-TV1-10_Prepare_Role.png)
- [Tags Prepare](../../evidence/TanPhat/Week_02/E-TV1-11_Prepare_Tags.png)
- [Bản ghi READY, dùng bản ảnh đã che taskToken](../../evidence/TanPhat/Week_02/E-TV1-12_Orders.png)

## Lambda fooddelivery-submit-transition – tiếp nhận chuyển trạng thái

- ARN: `arn:aws:lambda:us-east-1:053151184394:function:fooddelivery-submit-transition`.
- Tệp mã nguồn trên Console: lambda_function.py.
- Role: LabRole. Memory: 128 MB. Timeout: 20 giây.
- Biến môi trường: WORKFLOW_TASKS_TABLE = fooddelivery-workflow-tasks.
- Dữ liệu nghiệp vụ đầu vào gồm orderId, targetStatus, actorId và requestId.
- Chức năng: tiếp nhận yêu cầu chuyển trạng thái, claim bước chờ và gửi callback để workflow tiếp tục.
- Đã lưu các sự kiện w2_accept_phat, w2_deliver_phat và w2_complete_phat.
- Khi chạy lại toàn luồng, ba sự kiện dùng cùng mã đơn thực tế `TEST-W2-PHAT-001`. Sự kiện COMPLETED đã được cập nhật đồng bộ mã đơn.

### Minh chứng

- [Lambda Submit ban đầu](../../evidence/TanPhat/Week_02/E-TV1-13_CreateLambda.png)
- [Mã nguồn Submit](../../evidence/TanPhat/Week_02/E-TV1-14_Submit_Code.png)
- [Cấu hình Submit](../../evidence/TanPhat/Week_02/E-TV1-15_Submit_Config.png)
- [Biến môi trường Submit](../../evidence/TanPhat/Week_02/E-TV1-16_Submit_Environment.png)
- [Role Submit](../../evidence/TanPhat/Week_02/E-TV1-17_Submit_Role.png)
- [Tags Submit](../../evidence/TanPhat/Week_02/E-TV1-18_Submit_Tags.png)
- [Đầu vào ACCEPTED](../../evidence/TanPhat/Week_02/E-TV1-19_Submit_Event_Accept.png)
- [Đầu vào DELIVERING](../../evidence/TanPhat/Week_02/E-TV1-20_Submit_Event_Deliver.png)
- [Đầu vào COMPLETED](../../evidence/TanPhat/Week_02/E-TV1-21_Submit_Event_Complete.png)

## Lambda fooddelivery-commit-transition – cập nhật trạng thái đơn hàng

- ARN: `arn:aws:lambda:us-east-1:053151184394:function:fooddelivery-commit-transition`.
- Tệp mã nguồn trên Console: lambda_function.py.
- Role: LabRole. Memory: 128 MB. Timeout: 20 giây.
- Các biến môi trường: ORDERS_TABLE, WORKFLOW_TASKS_TABLE và SNS_TOPIC_ARN.
- Bảng đơn hàng: fooddelivery-orders.
- Mục đích: ghi nhận trạng thái đơn sau khi bước chờ tương ứng hoàn tất.
- Cập nhật status, updatedAt và lastTransitionRequestId.
- Khi chuyển sang ACCEPTED, gán driverId theo actorId của tài xế nhận đơn.
- Tăng version thêm 1 sau lần cập nhật hợp lệ.
- Bộ ảnh Phát xác nhận CommitAcceptedTransition thành công và workflow chuyển sang chờ DELIVERING.
- Kết quả soạn sẵn cho TC05 khi chạy đạt: Orders lần lượt có ACCEPTED, version 2. DELIVERING, version 3. COMPLETED, version 4. driverId giữ nguyên tài xế đã nhận đơn.
- Kết quả soạn sẵn cho TC06 khi chạy đạt: gửi lại cùng yêu cầu chuyển trạng thái không làm tăng version hoặc commit lần thứ hai.
- Kết quả soạn sẵn cho TC07 khi chạy đạt: yêu cầu dùng version hoặc trạng thái cũ bị từ chối và dữ liệu Orders giữ nguyên.
- Kết quả toàn luồng được đối chiếu bằng dữ liệu Orders và execution Succeeded của cùng mã đơn.

### Minh chứng

- [Mã nguồn Commit](../../evidence/TanPhat/Week_02/E-TV1-22_Commit_Code.png)
- [Cấu hình Commit](../../evidence/TanPhat/Week_02/E-TV1-23_Commit_Config.png)
- [Biến môi trường Commit](../../evidence/TanPhat/Week_02/E-TV1-24_Commit_Environment.png)
- [Biến môi trường SNS](../../evidence/TanPhat/Week_02/E-TV1-25_Commit_Environment_SNS.png)
- [Role Commit](../../evidence/TanPhat/Week_02/E-TV1-26_Commit_Role.png)
- [Tags Commit](../../evidence/TanPhat/Week_02/E-TV1-27_Commit_Tags.png)
- [Orders ACCEPTED, version 2](../../evidence/TanPhat/Week_02/E-TV1-28_TC05_Orders_Accepted.png)
- [Orders DELIVERING, version 3](../../evidence/TanPhat/Week_02/E-TV1-29_TC05_Orders_Delivering.png)
- [Orders COMPLETED, version 4](../../evidence/TanPhat/Week_02/E-TV1-30_TC05_Orders_Completed.png)
- [Toàn luồng hoàn tất Succeeded](../../evidence/TanPhat/Week_02/E-TV1-31_TC05_Workflow_Succeeded.png)

## SNS – cấu hình và kiểm thử thông báo

- Topic: fooddelivery-order-events. Loại: Standard.
- Topic ARN môi trường Phát: `arn:aws:sns:us-east-1:053151184394:fooddelivery-order-events`.
- Display name: FoodDelivery.
- Subscription EMAIL đã Confirmed.
- Publish thủ công và nhận email thử thành công với nội dung TEST-SNS-W2-PHAT.
- SNS_TOPIC_ARN đã được cấu hình trong Lambda Commit.
- Kết quả cho TC12: sau commit thành công, Lambda gửi thông báo chứa thông tin đơn hàng. Email được đối chiếu với đúng orderId và trạng thái đã ghi trong Orders.
- Email thử thủ công được giữ làm minh chứng cấu hình kênh gửi, không dùng thay email phát sinh sau commit.

### Minh chứng

- [Topic SNS](../../evidence/TanPhat/Week_02/E-TV1-32_SNS_Topic.png)
- [Subscription Confirmed](../../evidence/TanPhat/Week_02/E-TV1-33_SNS_Subscription.png)
- [Tags SNS](../../evidence/TanPhat/Week_02/E-TV1-34_SNS_Tags.png)
- [Publish thủ công thành công](../../evidence/TanPhat/Week_02/E-TV1-35_SNS_PublishTest.png)
- [Email thử thủ công](../../evidence/TanPhat/Week_02/E-TV1-36_SNS_EmailTest.png)
- [Orders đã commit](../../evidence/TanPhat/Week_02/E-TV1-37_TC12_Orders_Committed.png)
- [Log xác nhận commit và publish](../../evidence/TanPhat/Week_02/E-TV1-38_TC12_Commit_Publish_Log.png)
- [Email phát sinh sau commit](../../evidence/TanPhat/Week_02/E-TV1-39_TC12_SNS_AfterCommit_Email.png)

## Dữ liệu và kiểm thử backend bổ sung

- Dữ liệu ban đầu đã chụp: TEST-W2-PHAT-001, customerId C001, status PLACED, version 1, workflowStatus NOT_STARTED.
- Các lần thử bổ sung dùng đơn mới, ghi mã đơn và thời điểm thật trong ảnh.
- Mỗi ca đối chiếu cùng orderId từ yêu cầu, phản hồi, Orders và execution.
- Bảng dưới là kết quả thực tế đạt được:

| Mã | Nội dung | Kết quả dự kiến khi đạt | Minh chứng |
| --- | --- | --- | --- |
| TC05 | Luồng chuyển trạng thái hợp lệ. | ACCEPTED version 2, DELIVERING version 3, COMPLETED version 4. Tài xế được giữ nguyên. Execution Succeeded. | E-TV1-28_TC05_Orders_Accepted.png, E-TV1-29_TC05_Orders_Delivering.png, E-TV1-30_TC05_Orders_Completed.png, E-TV1-31_TC05_Workflow_Succeeded.png. |
| TC06 | Gửi lại cùng requestId chuyển trạng thái. | Không commit lần hai, không tăng version lần hai. Ghi đúng phản hồi thực tế của lần gửi lại. | E-TV1-41_TC06_Duplicate_Requests.png, E-TV1-42_TC06_Orders_Unchanged.png, E-TV1-43_TC06_Commit_History.png. |
| TC07 | Version hoặc trạng thái cũ. | Yêu cầu bị từ chối, không cập nhật Orders và không hoàn tất sai bước callback. | E-TV1-44_TC07_InvalidTransition_Response.png, E-TV1-45_TC07_StaleVersion_Response.png, E-TV1-46_TC07_Orders_Unchanged.png. |
| TC08 | Hai tài xế gửi yêu cầu nhận cùng đơn. | Chỉ một yêu cầu nhận thành công. Tài xế còn lại không ghi đè người nhận. | E-TV1-47_TC08_D001_Response.png, E-TV1-48_TC08_D002_Response.png, E-TV1-49_TC08_Orders_Winner.png. |
| TC09 | Hết thời gian chờ callback. | Execution kết thúc theo nhánh lỗi cấu hình. Có Error/Cause. Đơn không tự chuyển sang COMPLETED. | E-TV1-50_TC09_Execution_Error.png, E-TV1-51_TC09_Orders_AfterTimeout.png. |
| TC12 | SNS tự động sau commit. | Có commit thành công, publish và email chứa cùng orderId, trạng thái. | E-TV1-37_TC12_Orders_Committed.png, E-TV1-38_TC12_Commit_Publish_Log.png, E-TV1-39_TC12_SNS_AfterCommit_Email.png. |

### Minh chứng

- [Dữ liệu ban đầu](../../evidence/TanPhat/Week_02/E-TV1-40_Integration_Order_Initial.png)
- [TC06: hai lần gửi cùng yêu cầu](../../evidence/TanPhat/Week_02/E-TV1-41_TC06_Duplicate_Requests.png)
- [TC06: Orders không tăng version lần hai](../../evidence/TanPhat/Week_02/E-TV1-42_TC06_Orders_Unchanged.png)
- [TC06: lịch sử commit](../../evidence/TanPhat/Week_02/E-TV1-43_TC06_Commit_History.png)
- [TC07: phản hồi chuyển trạng thái sai](../../evidence/TanPhat/Week_02/E-TV1-44_TC07_InvalidTransition_Response.png)
- [TC07: phản hồi version cũ](../../evidence/TanPhat/Week_02/E-TV1-45_TC07_StaleVersion_Response.png)
- [TC07: Orders giữ nguyên](../../evidence/TanPhat/Week_02/E-TV1-46_TC07_Orders_Unchanged.png)
- [TC08: phản hồi tài xế D001](../../evidence/TanPhat/Week_02/E-TV1-47_TC08_D001_Response.png)
- [TC08: phản hồi tài xế D002](../../evidence/TanPhat/Week_02/E-TV1-48_TC08_D002_Response.png)
- [TC08: dữ liệu tài xế nhận thành công](../../evidence/TanPhat/Week_02/E-TV1-49_TC08_Orders_Winner.png)
- [TC09: execution và nguyên nhân lỗi](../../evidence/TanPhat/Week_02/E-TV1-50_TC09_Execution_Error.png)
- [TC09: Orders sau timeout](../../evidence/TanPhat/Week_02/E-TV1-51_TC09_Orders_AfterTimeout.png)

## Kiểm thử lại và tích hợp do Huy thực hiện

- Ngày thực hiện đã có minh chứng: 16/10/2026.
- Người triển khai lại backend và thao tác kiểm thử: Nguyễn Lê Huy – 24110221.
- Mục đích: tích hợp phần backend tuần 2 với giao diện khách hàng, tài xế và WebSocket.

### Luồng hợp lệ và gửi lặp tạo đơn

- Mã đơn: ORD-5646f576f13f227a66e63683.
- Hai yêu cầu createOrder cùng requestId f9bab3a4-e5f7-44e7-bd27-cceb9fc9adb9 trả về cùng orderId.
- Ghi nhận một execution tương ứng.
- D001 nhận đơn, bắt đầu giao và hoàn tất. Kết quả COMPLETED, version 4, driverId D001.
- Step Functions xác nhận Succeeded. Execution bắt đầu 16:05:04, kết thúc 16:08:23, UTC+7.
- Đây là kiểm thử gửi lặp tạo đơn. TC06 kiểm tra riêng yêu cầu chuyển trạng thái.

#### Minh chứng

- [Yêu cầu đầu](../../evidence/LeHuy/Week_02/CreateOrder_FirstRequest.png)
- [Gửi lại cùng yêu cầu](../../evidence/LeHuy/Week_02/CreateOrder_DuplicateRequest.png)
- [Execution tương ứng](../../evidence/LeHuy/Week_02/CreateOrder_DuplicateExecution.png)
- [Đơn hoàn tất](../../evidence/LeHuy/Week_02/DuplicateOrder_Final.png)
- [Execution Succeeded](../../evidence/LeHuy/Week_02/DuplicateOrder_Workflow_Succeeded.png)

### Hai tài xế nhận cùng đơn

- Mã đơn: ORD-8b651980f34813179dc05e55.
- D001 nhận thành công với ACCEPTED, version 2.
- D002 gửi updateOrderStatus, targetStatus ACCEPTED, expectedVersion 1 lúc 16:50:09.627, UTC+7.
- Phản hồi cùng requestId 31b46d5e-67c7-4f75-8af6-38822ef5dd76 lúc 16:50:10.371: ok = false, lỗi FORBIDDEN.
- Đơn được D001 xử lý đến COMPLETED, version 4 và workflowStatus SUCCEEDED.
- Ảnh cuối hiện có vẫn ghi executionStatus RUNNING tại thời điểm chụp. Chưa dùng ảnh này để khẳng định execution đã kết thúc.
- Kết luận trong phạm vi thử thủ công: D002 bị từ chối và không ghi đè tài xế D001.

#### Minh chứng

- [D001 nhận đơn](../../evidence/LeHuy/Week_02/ConcurrentAccept_D001.png)
- [Giao diện D002](../../evidence/LeHuy/Week_02/ConcurrentAccept_D002.png)
- [Yêu cầu và phản hồi từ chối D002](../../evidence/LeHuy/Week_02/ConcurrentAccept_D002_Response.png)
- [Đơn hoàn tất do D001 xử lý](../../evidence/LeHuy/Week_02/ConcurrentAccept_Final.png)

### Phân quyền khách hàng và tài xế

- Với đơn của C001, C002 bị từ chối getOrder và subscribeOrder bằng mã FORBIDDEN.
- Với đơn đã giao D001, D002 bị từ chối getOrder và subscribeOrder bằng mã FORBIDDEN.
- D001 đọc lại đơn thành công, nhận đúng COMPLETED, version 4 và driverId D001.

#### Minh chứng

- [C002 bị từ chối đọc](../../evidence/LeHuy/Week_02/Auth_C002_ReadDenied.png)
- [C002 bị từ chối theo dõi](../../evidence/LeHuy/Week_02/Auth_C002_SubscribeDenied.png)
- [D002 bị từ chối đọc](../../evidence/LeHuy/Week_02/Auth_D002_ReadDenied.png)
- [D002 bị từ chối theo dõi](../../evidence/LeHuy/Week_02/Auth_D002_SubscribeDenied.png)
- [D001 đọc đơn được giao](../../evidence/LeHuy/Week_02/Auth_D001_ReadAssignedOrder.png)

### Kết nối lại và nhận broadcast

- C001 ngắt kết nối lúc 16:20:50, kết nối lại lúc 16:21:08 và subscribeOrder thành công lúc 16:21:09, UTC+7.
- Lambda broadcast trả ok = true, sent = 1, skipped = 0, gone = 0.
- Khách nhận ORDER_UPDATED mới lúc 16:24:35 với đúng mã đơn đã hoàn tất, version 4 và driverId D001.
- Kết luận: kết nối mở lại và đăng ký theo dõi lại nhận được thông điệp mới.

#### Minh chứng

- [Kết nối và đăng ký lại](../../evidence/LeHuy/Week_02/Reconnect_Connection.png)
- [Kết quả Lambda broadcast](../../evidence/LeHuy/Week_02/Reconnect_BroadcastResult.png)
- [Thông điệp mới nhận được](../../evidence/LeHuy/Week_02/Reconnect_OrderUpdated.png)

### Lần thử execution thất bại trước đó

- Mã đơn: ORD-78d2a0494072dbc65c3322a4.
- Ảnh ghi nhận status PLACED, version 1, driverId null, executionStatus FAILED và workflowStatus còn NOT_STARTED.
- Danh sách execution ghi nhận Failed sau khoảng 5 phút.
- Đơn không tự hoàn tất. TC09 bổ sung Error/Cause và đối chiếu dữ liệu sau timeout.

#### Minh chứng

- [Đơn chưa hoàn tất khi execution FAILED](../../evidence/LeHuy/Week_02/DuplicateOrder_Timeout.png)
- [Danh sách execution](../../evidence/LeHuy/Week_02/DuplicateOrder_Workflow_Succeeded.png)

## Bàn giao và tổng kết

- Phần triển khai chính của Phát gồm workflow, ba Lambda Prepare, Submit, Commit và SNS.
- Huy đã triển khai lại và có kết quả tích hợp luồng hoàn tất, gửi lặp tạo đơn, phân quyền, thử nhận cùng đơn và kết nối lại.
- Mã nguồn và ASL được lưu về repository cùng các ảnh minh chứng.
- Trước khi nộp: kiểm tra toàn bộ link, che taskToken, xác nhận trạng thái tài nguyên và ghi chi phí theo số liệu thực tế.

### Minh chứng bàn giao bổ sung

- [Bản xuất workflow trong repository](../../evidence/TanPhat/Week_02/E-TV1-52_Git_Workflow_Source.png)
- [Mã nguồn ba Lambda trong repository](../../evidence/TanPhat/Week_02/E-TV1-53_Git_Lambda_Source.png)
