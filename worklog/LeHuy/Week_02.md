## Triển khai Lambda prepare-task của TV1 vào môi trường tích hợp
- Ngày thực hiện: 14/10/2026.
- Người triển khai AWS: Nguyễn Lê Huy – 24110221.
- Người phụ trách mã nguồn TV1: Trương Tấn Phát – 24110298.
- Region: us-east-1.
- Tên hàm: fooddelivery-prepare-task.
- Mã nguồn sử dụng: code/TanPhat/Week_02/fooddelivery-prepare-task/lambda_function.py.
- Công việc: triển khai mã TV1 vào tài khoản AWS của Huy để tích hợp hệ thống.
- Biến môi trường WORKFLOW_TASKS_TABLE: fooddelivery-workflow-tasks.
- Memory: 128 MB.
- Timeout: 20 giây.
- Execution role: LabRole.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Tag CodeAuthor: 24110298.
- Kết quả: đã cập nhật mã và cấu hình hàm.
- Phạm vi hoàn thành: triển khai và cấu hình. Chưa kiểm thử lưu bước chờ từ workflow trên tài khoản tích hợp.
### Minh chứng
- [Mã prepare-task đã triển khai](../../evidence/TanPhat/Week_02/Prepare_Code.png)
- [Biến môi trường](../../evidence/TanPhat/Week_02/Prepare_Environment.png)
- [Bộ nhớ và timeout](../../evidence/TanPhat/Week_02/Prepare_Config.png)
- [Execution role](../../evidence/TanPhat/Week_02/Prepare_Role.png)
- [Tag của Lambda](../../evidence/TanPhat/Week_02/Prepare_Tags.png)

## Triển khai Lambda submit-transition vào môi trường tích hợp
- Ngày thực hiện: 14/10/2026.
- Người triển khai AWS: Nguyễn Lê Huy – 24110221.
- Người phụ trách mã nguồn TV1: Trương Tấn Phát – 24110298.
- Region: us-east-1.
- Tên hàm: fooddelivery-submit-transition.
- Mã nguồn: code/TanPhat/Week_02/fooddelivery-submit-transition/lambda_function.py.
- Runtime: Python 3.13.
- Execution role: LabRole.
- Memory: 128 MB.
- Timeout: 20 giây.
- Biến môi trường WORKFLOW_TASKS_TABLE: fooddelivery-workflow-tasks.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Tag CodeAuthor: 24110298.
- Mục đích: tiếp nhận yêu cầu chuyển trạng thái, claim bước chờ và gửi callback cho Step Functions.
- Kết quả: đã Deploy mã và lưu cấu hình.
- Phạm vi: hoàn thành triển khai, chưa kiểm thử callback trên tài khoản tích hợp.
### Minh chứng
- [Execution role](../../evidence/TanPhat/Week_02/Submit_Role.png)
- [Mã nguồn đã triển khai](../../evidence/TanPhat/Week_02/Submit_Code.png)
- [Biến môi trường](../../evidence/TanPhat/Week_02/Submit_Environment.png)
- [Bộ nhớ và timeout](../../evidence/TanPhat/Week_02/Submit_Config.png)
- [Tag Lambda](../../evidence/TanPhat/Week_02/Submit_Tags.png)

## Triển khai Lambda commit-transition vào môi trường tích hợp
- Ngày thực hiện: 14/10/2026.
- Người triển khai AWS: Nguyễn Lê Huy – 24110221.
- Người phụ trách mã nguồn TV1: Trương Tấn Phát – 24110298.
- Region: us-east-1.
- Tên hàm: fooddelivery-commit-transition.
- Mã nguồn: code/TanPhat/Week_02/fooddelivery-commit-transition/lambda_function.py.
- Runtime: Python 3.13.
- Execution role: LabRole.
- Memory: 128 MB.
- Timeout: 20 giây.
- Biến môi trường ORDERS_TABLE: fooddelivery-orders.
- Biến môi trường WORKFLOW_TASKS_TABLE: fooddelivery-workflow-tasks.
- SNS_TOPIC_ARN: chưa cấu hình, sẽ bổ sung topic của tài khoản tích hợp.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Tag CodeAuthor: 24110298.
- Mục đích: cập nhật Orders và đánh dấu bước đã xử lý sau callback.
- Kết quả: đã Deploy mã và lưu cấu hình hai bảng.
- Phạm vi: chưa kiểm thử commit qua workflow và chưa kiểm thử SNS trong môi trường tích hợp.
### Minh chứng
- [Execution role](../../evidence/TanPhat/Week_02/Commit_Role.png)
- [Mã nguồn đã triển khai](../../evidence/TanPhat/Week_02/Commit_Code.png)
- [Biến môi trường](../../evidence/TanPhat/Week_02/Commit_Environment.png)
- [Bộ nhớ và timeout](../../evidence/TanPhat/Week_02/Commit_Config.png)
- [Tag Lambda](../../evidence/TanPhat/Week_02/Commit_Tags.png)

## Dựng SNS và cấu hình thông báo cho Lambda commit
- Ngày thực hiện: 14/10/2026.
- Người triển khai: Nguyễn Lê Huy – 24110221.
- Hạng mục phối hợp: triển khai phần thông báo của TV1 vào tài khoản tích hợp.
- Region: us-east-1.
- Topic: fooddelivery-order-events.
- Type: Standard.
- Display name: FoodDelivery.
- Topic ARN: arn:aws:sns:us-east-1:165662523632:fooddelivery-order-events.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Subscription: Email, đã xác nhận.
- Kiểm thử: publish thông báo TEST-SNS-W2-HUY từ SNS Console.
- Kết quả publish: thành công.
- Kết quả nhận email: nhận đúng nội dung kiểm thử.
- Lambda được cấu hình: fooddelivery-commit-transition.
- Đã bổ sung SNS_TOPIC_ARN, giữ nguyên ORDERS_TABLE và WORKFLOW_TASKS_TABLE.
- Phạm vi: đã kiểm thử SNS Console gửi email. Chưa kiểm thử Lambda commit gửi SNS qua workflow.
### Minh chứng
- [Thông tin topic](../../evidence/TanPhat/Week_02/SNS_Topic.png)
- [Tag topic](../../evidence/TanPhat/Week_02/SNS_Tags.png)
- [Subscription đã xác nhận](../../evidence/TanPhat/Week_02/SNS_Subscription.png)
- [Publish thông báo thử](../../evidence/TanPhat/Week_02/SNS_PublishTest.png)
- [Email thực nhận](../../evidence/TanPhat/Week_02/SNS_EmailTest.png)
- [Biến môi trường commit có SNS](../../evidence/TanPhat/Week_02/Commit_Environment_SNS.png)

## Triển khai workflow TV1 vào tài khoản tích hợp
- Ngày thực hiện: 14/10/2026.
- Người triển khai: Nguyễn Lê Huy – 24110221.
- Người phụ trách mã workflow TV1: Trương Tấn Phát – 24110298.
- Account ID triển khai: 165662523632.
- Region: us-east-1.
- Tên state machine: fooddelivery-order-workflow.
- State machine ARN: arn:aws:sns:us-east-1:165662523632:fooddelivery-order-events.
- Type: Standard.
- Execution role: LabRole.
- QueryLanguage: JSONPath.
- Tệp nguồn TV1: config/TanPhat/Week_02/order_workflow.asl.json.
- Tệp cấu hình tích hợp: config/LeHuy/Week_02/order_workflow.asl.json.
- Điều chỉnh triển khai: thay Account ID trong ARN Lambda từ tài khoản Phát sang tài khoản Huy.
- Luồng: chờ nhận đơn, commit nhận đơn, chờ giao hàng, commit giao hàng, chờ hoàn tất và commit hoàn tất.
- Timeout: 300 giây cho mỗi Task chờ callback.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Tag CodeAuthor: 24110298.
- Kết quả: đã lưu định nghĩa và cấu hình workflow.
- Phạm vi: chưa chạy execution và chưa xác nhận luồng nghiệp vụ thành công trên tài khoản tích hợp.
### Minh chứng
- [Cấu hình workflow](../../evidence/TanPhat/Week_02/Workflow_Config.png)
- [Execution role](../../evidence/TanPhat/Week_02/Workflow_Role.png)
- [Tag workflow](../../evidence/TanPhat/Week_02/Workflow_Tags.png)

## Chuẩn bị dữ liệu kiểm thử workflow tích hợp
- Ngày thực hiện: 15/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Bảng: fooddelivery-orders.
- Order ID: TEST-W2-HUY-001.
- Customer ID: C001.
- Trạng thái ban đầu: PLACED.
- WorkflowStatus ban đầu: NOT_STARTED.
- Version: Number, giá trị 1.
- Kiểm tra dữ liệu: Query tìm thấy đúng đơn thử.
- Lambda chuẩn bị sự kiện: fooddelivery-submit-transition.
- Đã lưu ba private test event: w2_accept_huy, w2_deliver_huy, w2_complete_huy.
- Actor mô phỏng: DRIVER-01.
- Cấu trúc sự kiện: theo mã submit hiện tại của TV1.
- Phạm vi: tạo đơn thủ công và chuẩn bị sự kiện. Chưa chạy workflow, chưa kiểm thử từ giao diện web.
### Minh chứng
- [Đơn ban đầu PLACED, version 1](../../evidence/TanPhat/Week_02/Integration_Order_Initial.png)
- [Sự kiện nhận đơn](../../evidence/TanPhat/Week_02/Submit_Event_Accept.png)
- [Sự kiện bắt đầu giao](../../evidence/TanPhat/Week_02/Submit_Event_Deliver.png)
- [Sự kiện hoàn tất](../../evidence/TanPhat/Week_02/Submit_Event_Complete.png)

## Kiểm thử thành công workflow TV1 trên tài khoản tích hợp
- Ngày thực hiện: 15/10/2026.
- Người triển khai và thao tác kiểm thử: Nguyễn Lê Huy – 24110221.
- Người phụ trách phần workflow TV1: Trương Tấn Phát – 24110298.
- Account ID: 165662523632.
- Region: us-east-1.
- Workflow: fooddelivery-order-workflow.
- Execution: huy-w2-002.
- Thời điểm bắt đầu execution: 13:29:21, UTC+7.
- Order ID: TEST-W2-HUY-002.
- Cách kiểm thử: tạo đơn thủ công, Start execution và gửi các sự kiện từ Lambda Console.
- Workflow đã đi qua các bước nhận đơn, bắt đầu giao và hoàn tất.
- Kết quả cuối trong Orders: status COMPLETED, version 4.
- Driver ID: DRIVER-01.
- LastTransitionRequestId: HUY-W2-COMPLETE-002.
- Graph kết thúc thành công tại OrderCompletedSucceed.
- SNS ACCEPTED: đã nhận email lúc 13:32.
- SNS COMPLETED: đã nhận email lúc 13:37.
- Điều chỉnh trong quá trình tích hợp: sửa mã submit và commit với hỗ trợ của AI. Cần đồng bộ bản mã đã triển khai cho TV1 rà soát và cập nhật Git.
- Kết quả: luồng nghiệp vụ cơ bản của TV1 chạy thành công trên tài khoản tích hợp.
- Phạm vi: kiểm thử backend bằng sự kiện mô phỏng. Chưa kiểm thử tạo đơn từ web, cập nhật qua WebSocket, tranh nhận đơn, gửi lặp và timeout.
### Minh chứng
- [Workflow đang chờ nhận đơn](../../evidence/LeHuy/Week_02/Integration_002_Waiting.png)
- [Orders sau nhận đơn](../../evidence/LeHuy/Week_02/Integration_002_Accepted.png)
- [Orders đang giao](../../evidence/LeHuy/Week_02/Integration_002_Delivering.png)
- [Orders hoàn tất](../../evidence/LeHuy/Week_02/Integration_002_Completed.png)
- [Workflow hoàn tất thành công](../../evidence/LeHuy/Week_02/Integration_002_Succeeded.png)
- [Email nhận đơn](../../evidence/LeHuy/Week_02/Integration_002_SNS_Accepted.png)
- [Email hoàn tất](../../evidence/LeHuy/Week_02/Integration_002_SNS_Completed.png)

## Triển khai Lambda broadcast cho WebSocket
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Tên hàm: fooddelivery-broadcast.
- Runtime: Python 3.13.
- Handler: lambda_function.lambda_handler.
- Execution role: LabRole.
- Memory: 128 MB.
- Timeout: 20 giây.
- ORDERS_TABLE: fooddelivery-orders.
- CONNECTIONS_TABLE: fooddelivery-connections.
- TASKS_TABLE: fooddelivery-workflow-tasks.
- WS_ENDPOINT_URL: https://lob1j5l21i.execute-api.us-east-1.amazonaws.com/dev/.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Mục đích: gửi ORDER_UPDATED đến các kết nối đang theo dõi đơn hàng.
- Kết quả: đã tải mã và lưu cấu hình.
- Phạm vi: chưa kiểm thử gửi tin đến trình duyệt và chưa nối broadcast vào workflow.
### Minh chứng
- [Stage WebSocket](../../evidence/LeHuy/Week_02/WebSocket_Stage.png)
- [Execution role](../../evidence/LeHuy/Week_02/Broadcast_Role.png)
- [Mã broadcast](../../evidence/LeHuy/Week_02/Broadcast_Code.png)
- [Biến môi trường](../../evidence/LeHuy/Week_02/Broadcast_Environment.png)
- [Bộ nhớ và timeout](../../evidence/LeHuy/Week_02/Broadcast_Config.png)
- [Tag broadcast](../../evidence/LeHuy/Week_02/Broadcast_Tags.png)

## Triển khai Lambda WebSocket dispatcher
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Tên hàm: fooddelivery-ws-dispatcher.
- Runtime: Python 3.13.
- Handler: lambda_function.lambda_handler.
- Execution role: LabRole.
- Memory: 128 MB.
- Timeout: 20 giây.
- ORDERS_TABLE: fooddelivery-orders.
- CONNECTIONS_TABLE: fooddelivery-connections.
- TASKS_TABLE: fooddelivery-workflow-tasks.
- STATE_MACHINE_ARN: arn:aws:states:us-east-1:165662523632:stateMachine:fooddelivery-order-workflow.
- SUBMIT_LAMBDA_ARN: arn:aws:lambda:us-east-1:165662523632:function:fooddelivery-submit-transition.
- Mã dispatcher đã điều chỉnh để trao đổi dữ liệu với submit của TV1 qua actorId và phản hồi status/errorCode.
- SESSION_TOKENS_JSON: chưa cấu hình.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Kết quả: đã tải mã và lưu cấu hình.
- Phạm vi: chưa tích hợp dispatcher vào các route WebSocket và chưa kiểm thử từ trình duyệt.
### Minh chứng
- [Execution role](../../evidence/LeHuy/Week_02/Dispatcher_Role.png)
- [Mã dispatcher](../../evidence/LeHuy/Week_02/Dispatcher_Code.png)
- [Biến môi trường](../../evidence/LeHuy/Week_02/Dispatcher_Environment.png)
- [Bộ nhớ và timeout](../../evidence/LeHuy/Week_02/Dispatcher_Config.png)
- [Tag dispatcher](../../evidence/LeHuy/Week_02/Dispatcher_Tags.png)

## Cấu hình phiên demo và tích hợp dispatcher vào WebSocket
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Lambda: fooddelivery-ws-dispatcher.
- Đã tạo token phiên demo cho khách C001, C002 và tài xế D001, D002.
- Đã cấu hình SESSION_TOKENS_JSON trên dispatcher.
- Đã thêm quy tắc *.local.json vào .gitignore.
- Không đưa token vào Git hoặc ảnh minh chứng.
- API: fooddelivery-ws.
- Route selection expression: $request.body.action.
- Đã chuyển tích hợp của $connect, $disconnect và $default sang fooddelivery-ws-dispatcher.
- Đã Deploy API vào stage dev.
- Kết quả: hoàn thành cấu hình phiên và triển khai tích hợp API.
- Phạm vi: phiên demo do backend quản lý, chưa phải xác thực người dùng hoàn chỉnh. Chưa kiểm thử kết nối và nghiệp vụ từ trình duyệt.
### Minh chứng
- [Route connect](../../evidence/LeHuy/Week_02/Dispatcher_Route_Connect.png)
- [Route disconnect](../../evidence/LeHuy/Week_02/Dispatcher_Route_Disconnect.png)
- [Route default](../../evidence/LeHuy/Week_02/Dispatcher_Route_Default.png)
- [Deploy stage dev](../../evidence/LeHuy/Week_02/Dispatcher_Stage_Deploy.png)

## Kiểm thử giao diện WebSocket và gửi cập nhật qua broadcast
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Giao diện: customer.html, driver.html và shared.js.
- Khách thử: C001.
- Tài xế thử: D001.
- Hai giao diện kết nối OPEN và nhận phản hồi pong.
- Khách C001 subscribe đơn TEST-W2-HUY-002 thành công.
- Dữ liệu đơn hiển thị: COMPLETED, version 4.
- Đã gọi fooddelivery-broadcast bằng sự kiện chứa orderId.
- Kết quả broadcast: ok = true, sent = 1.
- Trang khách nhận tin ORDER_UPDATED đúng đơn, trạng thái và version.
- Phạm vi: kiểm thử đọc/subscribe và gửi tin qua WebSocket bằng lệnh gọi broadcast thủ công.
### Minh chứng
- [Khách kết nối và nhận pong](../../evidence/LeHuy/Week_02/Customer_Connected.png)
- [Tài xế kết nối và nhận pong](../../evidence/LeHuy/Week_02/Driver_Connected.png)
- [Khách theo dõi đơn](../../evidence/LeHuy/Week_02/Customer_Subscribe.png)
- [Kết quả broadcast](../../evidence/LeHuy/Week_02/Broadcast_SendTest.png)
- [Khách nhận ORDER_UPDATED](../../evidence/LeHuy/Week_02/Customer_OrderUpdated.png)

## Tích hợp tạo đơn và cập nhật trạng thái từ giao diện WebSocket
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Phối hợp phần workflow TV1: Trương Tấn Phát – 24110298.
- Đã bổ sung gọi broadcast sau ba bước commit trong workflow.
- Tệp cấu hình: config/LeHuy/Week_02/order_workflow_realtime.asl.json.
- Khách thử: C001. Tài xế thử: D001.
- Order ID: ORD-f86fedeb4517961ca8402e48.
- Tạo đơn từ customer.html: thành công. Đơn được tạo với trạng thái PLACED, version = 1. Giao diện đăng ký theo dõi đơn thành công.
- Nhận/giao/hoàn tất từ driver.html: thành công. Tài xế D001 thực hiện lần lượt các bước ACCEPTED → DELIVERING → COMPLETED.
- Khách tự nhận ORDER_UPDATED ở ba mốc:
  - ACCEPTED, version = 2, driverId = D001. Thời điểm nhận: 15:28:45 ngày 16/10/2026, UTC+7.
  - DELIVERING, version = 3, driverId = D001. Thời điểm nhận: 15:30:04 ngày 16/10/2026, UTC+7.
  - COMPLETED, version = 4, driverId = D001. Thời điểm nhận: 15:31:28 ngày 16/10/2026, UTC+7.
- Trạng thái/version cuối: COMPLETED, version = 4. Đã Query bảng fooddelivery-orders và xác nhận dữ liệu khớp với giao diện.
- Trường workflowStatus trong bản ghi Orders: SUCCEEDED.
- Kết quả execution: Succeeded. Đã kiểm tra execution của đơn ORD-f86fedeb4517961ca8402e48 trên Step Functions Console. Workflow kết thúc tại OrderCompletedSucceed.- Phạm vi: kiểm thử luồng cơ bản qua WebSocket bằng phiên demo. Giao diện được mở từ máy cá nhân và kết nối tới backend trên AWS.
### Minh chứng
- [Workflow có broadcast](../../evidence/LeHuy/Week_02/Workflow_Broadcast_Definition.png)
- [Tạo đơn từ web](../../evidence/LeHuy/Week_02/Web_CreateOrder.png)
- [Cập nhật ACCEPTED](../../evidence/LeHuy/Week_02/Web_Realtime_Accepted.png)
- [Cập nhật DELIVERING](../../evidence/LeHuy/Week_02/Web_Realtime_Delivering.png)
- [Cập nhật COMPLETED](../../evidence/LeHuy/Week_02/Web_Realtime_Completed.png)
- [Dữ liệu cuối](../../evidence/LeHuy/Week_02/Web_Order_Final.png)
- [Execution hoàn tất](../../evidence/LeHuy/Week_02/Web_Workflow_Succeeded.png)

## Kiểm thử gửi lặp yêu cầu tạo đơn
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Khách thử: C001. Tài xế thử: D001.
- Mã đơn: ORD-5646f576f13f227a66e63683.
- Thao tác: tạo đơn một lần từ customer.html, sau đó sử dụng nút Gửi lại cùng yêu cầu.
- Request ID của cả hai lần gửi: f9bab3a4-e5f7-44e7-bd27-cceb9fc9adb9.
- Thời điểm gửi yêu cầu đầu: 16:05:05 ngày 16/10/2026, UTC+7.
- Thời điểm gửi lại: 16:06:32 ngày 16/10/2026, UTC+7.
- Kết quả phản hồi: cả hai lần đều trả về ok = true và cùng orderId = ORD-5646f576f13f227a66e63683.
- Trạng thái sau khi gửi lại: PLACED, version = 1. Thời điểm updatedAt giữ nguyên so với phản hồi tạo đơn ban đầu.
- Kiểm tra danh sách Step Functions: ghi nhận một execution mang tên mã đơn kiểm thử.
- Sau kiểm thử gửi lặp, tài xế D001 thực hiện nhận đơn, bắt đầu giao và hoàn tất.
- Kết quả cuối trên giao diện: COMPLETED, version = 4, driverId = D001, workflowStatus = SUCCEEDED.
- Kết quả execution trên Step Functions: Succeeded.
- Execution bắt đầu lúc 16:05:04 và kết thúc lúc 16:08:23 ngày 16/10/2026, UTC+7.
- Kết luận: trong lần thử này, gửi lại cùng requestId trả về đơn hàng đã tạo, không ghi nhận đơn hàng hoặc execution mới do lần gửi lại. Đơn tiếp tục được xử lý đến khi hoàn tất.
### Minh chứng
- [Yêu cầu tạo đơn ban đầu](../../evidence/LeHuy/Week_02/CreateOrder_FirstRequest.png)
- [Gửi lại cùng yêu cầu](../../evidence/LeHuy/Week_02/CreateOrder_DuplicateRequest.png)
- [Execution tương ứng với đơn](../../evidence/LeHuy/Week_02/CreateOrder_DuplicateExecution.png)
- [Đơn hoàn tất sau kiểm thử](../../evidence/LeHuy/Week_02/DuplicateOrder_Final.png)
- [Execution thành công](../../evidence/LeHuy/Week_02/DuplicateOrder_Workflow_Succeeded.png)

## Kiểm thử phân quyền truy cập đơn hàng giữa hai khách hàng
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Chủ đơn hàng: C001.
- Khách thực hiện truy cập chéo: C002.
- Mã đơn kiểm thử: ORD-5646f576f13f227a66e63683.
- Mục đích: kiểm tra khách hàng không được đọc hoặc đăng ký theo dõi đơn của khách hàng khác.
- Sử dụng kết nối WebSocket của phiên demo C002 để thực hiện kiểm thử.
- Kiểm thử đọc đơn: gửi yêu cầu getOrder với mã đơn của C001.
- Kết quả đọc đơn: backend trả về ok = false, mã lỗi FORBIDDEN. Phản hồi không chứa dữ liệu đơn hàng.
- Thời điểm nhận phản hồi đọc đơn: 16:17:11 ngày 16/10/2026, UTC+7.
- Kiểm thử theo dõi đơn: gửi yêu cầu subscribeOrder với cùng mã đơn.
- Kết quả theo dõi đơn: backend trả về ok = false, mã lỗi FORBIDDEN.
- Thời điểm nhận phản hồi theo dõi đơn: 16:17:54 ngày 16/10/2026, UTC+7.
- Kết luận: trong lần thử này, backend từ chối cả yêu cầu đọc và đăng ký theo dõi đơn của C001 từ phiên C002.
- Phạm vi: kiểm thử quyền truy cập chéo giữa hai khách hàng bằng phiên demo.
### Minh chứng
- [C002 bị từ chối đọc đơn của C001](../../evidence/LeHuy/Week_02/Auth_C002_ReadDenied.png)
- [C002 bị từ chối theo dõi đơn của C001](../../evidence/LeHuy/Week_02/Auth_C002_SubscribeDenied.png)

## Kiểm thử phân quyền truy cập đơn hàng giữa hai tài xế
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Mã đơn kiểm thử: ORD-5646f576f13f227a66e63683.
- Tài xế được giao đơn: D001.
- Tài xế kiểm thử truy cập chéo: D002.
- Mục đích: kiểm tra tài xế khác không được đọc hoặc đăng ký theo dõi đơn đã giao cho D001.
- Ngắt kết nối hiện tại và kết nối lại bằng phiên demo D002.
- Thực hiện getOrder với mã đơn kiểm thử.
- Kết quả đọc đơn: backend trả về ok = false, mã lỗi FORBIDDEN. Phản hồi không chứa dữ liệu đơn hàng.
- Tiếp tục thực hiện subscribeOrder bằng phiên D002.
- Kết quả theo dõi đơn: backend trả về ok = false, mã lỗi FORBIDDEN.
- Ngắt kết nối D002 và kết nối lại bằng phiên D001 để đối chiếu.
- Kết quả đối chiếu: getOrder trả về ok = true, status = COMPLETED, version = 4, driverId = D001 và executionStatus = SUCCEEDED.
- Nhật ký ghi nhận yêu cầu subscribeOrder của D001 thành công.
- Kết luận: trong lần thử này, backend từ chối yêu cầu đọc và theo dõi đơn của D002, đồng thời cho phép tài xế được giao đơn D001 truy cập.
- Phạm vi: kiểm thử quyền truy cập trên đơn đã hoàn tất bằng hai phiên demo tài xế. Chưa kiểm thử hai tài xế tranh nhận đơn đồng thời.
### Minh chứng
- [D002 bị từ chối đọc đơn của D001](../../evidence/LeHuy/Week_02/Auth_D002_ReadDenied.png)
- [D002 bị từ chối theo dõi đơn của D001](../../evidence/LeHuy/Week_02/Auth_D002_SubscribeDenied.png)
- [D001 đọc đơn được giao thành công](../../evidence/LeHuy/Week_02/Auth_D001_ReadAssignedOrder.png)

## Kiểm thử kết nối lại và đăng ký theo dõi lại đơn hàng
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Khách hàng kiểm thử: C001.
- Mã đơn kiểm thử: ORD-5646f576f13f227a66e63683.
- Mục đích: kiểm tra khả năng nhận thông điệp cập nhật sau khi khách hàng ngắt kết nối, kết nối lại và đăng ký theo dõi lại đơn hàng.
- Trên customer.html, chủ động ngắt kết nối WebSocket rồi kết nối lại bằng phiên demo C001.
- Nhật ký ghi nhận kết nối CLOSED lúc 16:20:50 và OPEN trở lại lúc 16:21:08 ngày 16/10/2026, UTC+7.
- Sau khi kết nối mở lại, giao diện gửi yêu cầu subscribeOrder với mã đơn kiểm thử.
- Kết quả đăng ký theo dõi lại: backend trả về ok = true lúc 16:21:09, status = COMPLETED, version = 4 và driverId = D001.
- Tiếp tục gửi yêu cầu subscribeOrder lúc 16:21:19. Backend trả về ok = true lúc 16:21:20.
- Giữ kết nối khách hàng đang mở và kiểm thử Lambda fooddelivery-broadcast bằng sự kiện reconnect_existing_order với mã đơn kiểm thử.
- Kết quả thực thi Lambda: Succeeded.
- Phản hồi Lambda: ok = true, sent = 1, skipped = 0 và gone = 0.
- Nhật ký phía khách hàng ghi nhận thông điệp RECEIVED mới lúc 16:24:35 ngày 16/10/2026, UTC+7.
- Nội dung thông điệp: type = ORDER_UPDATED, orderId = ORD-5646f576f13f227a66e63683, status = COMPLETED, version = 4, driverId = D001 và workflowStatus = SUCCEEDED.
- Kết luận: trong lần thử này, khách hàng kết nối lại và đăng ký theo dõi lại thành công. Kết nối sau khi mở lại nhận được thông điệp ORDER_UPDATED do Lambda broadcast gửi.
- Phạm vi: kiểm thử kết nối lại bằng thao tác thủ công và đăng ký theo dõi lại đơn hàng. Sử dụng đơn đã hoàn tất và gọi Lambda để phát lại trạng thái hiện tại. Chưa kiểm thử tự động kết nối lại khi mất mạng hoặc tự động khôi phục đăng ký theo dõi.
### Minh chứng
- [Kết nối lại và đăng ký theo dõi đơn](../../evidence/LeHuy/Week_02/Reconnect_Connection.png)
- [Kết quả gọi Lambda broadcast](../../evidence/LeHuy/Week_02/Reconnect_BroadcastResult.png)
- [Thông điệp cập nhật nhận sau khi kết nối lại](../../evidence/LeHuy/Week_02/Reconnect_OrderUpdated.png)

## Kiểm thử thao tác nhận cùng một đơn trên hai phiên tài xế
- Ngày thực hiện: 16/10/2026.
- Người thực hiện: Nguyễn Lê Huy – 24110221.
- Region: us-east-1.
- Mã đơn kiểm thử: ORD-8b651980f34813179dc05e55.
- Hai tài xế tham gia: D001 và D002.
- Mục đích: kiểm tra thao tác nhận cùng một đơn trên hai phiên tài xế và đối chiếu tài xế được giao đơn.
- Mở hai giao diện driver.html bằng hai phiên demo D001 và D002, cùng chọn mã đơn kiểm thử.
- Kết quả phía D001: giao diện nhận thông điệp ORDER_UPDATED với status = ACCEPTED, version = 2 và driverId = D001.
- Sau khi nhận đơn, phía D001 ghi nhận readySteps chứa DELIVERING và nút Bắt đầu giao được bật.
- Kết quả phía D002: tại thời điểm chụp, các nút Nhận đơn, Bắt đầu giao và Hoàn tất đều bị khóa.
- Dữ liệu đang hiển thị phía D002 còn ở status = PLACED, version = 1, driverId = null và readySteps rỗng.
- Minh chứng hiện tại chưa thể hiện yêu cầu nhận đơn của D002 hoặc phản hồi từ chối tương ứng.
- Tài xế D001 tiếp tục thực hiện bắt đầu giao và hoàn tất đơn.
- Kết quả cuối trên giao diện: status = COMPLETED, version = 4, driverId = D001 và workflowStatus = SUCCEEDED.
- Tại thời điểm chụp kết quả cuối, executionStatus vẫn hiển thị RUNNING. Chưa đối chiếu trạng thái execution cuối trên Step Functions Console.
- Kết luận: ghi nhận D001 nhận và xử lý đơn đến trạng thái hoàn tất. Chưa đủ minh chứng để kết luận backend xử lý đúng hai yêu cầu nhận đơn cạnh tranh đồng thời.
- Phạm vi: kiểm thử thủ công trên hai giao diện tài xế. Cần bổ sung nhật ký yêu cầu và phản hồi của cả hai tài xế để đánh giá xử lý cạnh tranh.
### Minh chứng
- [D001 nhận đơn thành công](../../evidence/LeHuy/Week_02/ConcurrentAccept_D001.png)
- [Trạng thái giao diện D002 trong lần thử](../../evidence/LeHuy/Week_02/ConcurrentAccept_D002.png)
- [D001 hoàn tất đơn](../../evidence/LeHuy/Week_02/ConcurrentAccept_Final.png)