# KẾT QUẢ KIỂM THỬ TUẦN 3 – FOODDELIVERYREALTIME

- **Thời gian:** 19/10/2026 – 25/10/2026.
- **TV1:** Trương Tấn Phát – MSSV 24110298.
- **TV2:** Nguyễn Lê Huy – MSSV 24110221.
- **Môi trường triển khai:** AWS `us-east-1`.
- **Người tổng hợp:** Nguyễn Lê Huy.

## 1. Căn cứ tổng hợp

- [Kế hoạch tuần 3](../../TaskAssignments/Week_03.md).
- [Worklog TV1](../../worklog/TanPhat/Week_03.md).
- [Worklog TV2](../../worklog/LeHuy/Week_03.md).
- [Minh chứng TV1](../../evidence/TanPhat/Week_03/).
- [Minh chứng TV2](../../evidence/LeHuy/Week_03/).
- [Tài liệu triển khai và vận hành](../../design/Week_03/deployment.md).

Kết quả kiểm thử được tổng hợp từ worklog và minh chứng của hai thành viên. TV1 thực hiện kiểm thử workflow, callback, cập nhật dữ liệu và SNS. TV2 thực hiện kiểm thử giao diện, WebSocket, reconnect, phân quyền và tích hợp hệ thống. Các ca ghi “Đạt theo kết quả TV1” được dẫn theo hồ sơ TV1 bàn giao; TV2 chưa chạy lại độc lập toàn bộ các ca này.

## 2. Bảng kết quả kiểm thử

| Mã | Nội dung | Trạng thái | Kết quả |
| --- | --- | --- | --- |
| W3-TC01 | Luồng tạo đơn đến hoàn tất | Đạt trong lần hồi quy trước sửa workflow | C001/D001 tạo, nhận, giao và hoàn tất đơn ORD-dcba07009952a36dee9e01f4: COMPLETED version 4, driverId D001, workflowStatus và executionStatus SUCCEEDED. Lần hồi quy này diễn ra sau cập nhật dispatcher nhưng trước PersistWorkflowFailure. Orders, WorkflowTasks và SNS được dẫn theo hồ sơ TV1. |
| W3-TC02 | Gửi lại cùng requestId | Đạt theo kết quả TV1 | Yêu cầu đã hoàn tất trả ALREADY_DONE. Version giữ nguyên và không phát thêm SNS trong trường hợp gửi lặp đã kiểm thử. |
| W3-TC03 | Version cũ và khôi phục giao diện | Đạt trong phạm vi đã thử | Backend trả CONFLICT cho expectedVersion cũ. Giao diện đọc lại snapshot, khôi phục nút; đơn ORD-efa289eb56e757c8cac3bb98 tiếp tục chuyển DELIVERING version 3 bằng yêu cầu hợp lệ. Polling vẫn bật, chưa kiểm thử tách riêng khi tắt polling. |
| W3-TC04 | Chuyển sai bước hoặc cập nhật sau hoàn tất | Đạt theo kết quả TV1 | Yêu cầu không hợp lệ bị từ chối. Dữ liệu không bị chuyển sai trạng thái. |
| W3-TC05 | Callback sai hoặc gọi lại | Đạt theo kết quả TV1 | Callback sai bị từ chối. Gọi lại Submit/Commit không tạo thêm chuyển trạng thái trong các trường hợp đã kiểm thử. |
| W3-TC06 | Lưu trạng thái timeout sau sửa | Đạt trên đơn mới tại bước chờ nhận đơn | ORD-381e33d0155909969f8f2d98 không được nhận, PrepareAcceptedTask timeout 300 giây. HandleTimeout → PersistWorkflowFailure (thành công) → WorkflowFailed. Orders và snapshot tài xế giữ PLACED version 1, workflowStatus TIMED_OUT; Orders có workflowEndedAt. ExecutionStatus FAILED theo state Fail, readySteps rỗng và nút bị khóa. Yêu cầu đến trễ chỉ dẫn theo kết quả TV1. |
| W3-TC07 | Đơn đổi trạng thái khi khách offline | Đạt trong tình huống đã thử | ORD-071dc67f107f9beb266a21e4 được tài xế nhận trong lúc khách offline. Sau reconnect, khách nhận ACCEPTED version 2 và tiếp tục nhận DELIVERING version 3. Ngắt chủ động và khôi phục theo dõi được ghi tại worklog TV2. |
| W3-TC08 | Tải lại trang | Đạt | Mã đơn được khôi phục sau F5. Sau khi nhập phiên hợp lệ và kết nối lại, giao diện nhận snapshot hiện tại. |
| W3-TC09 | Sự kiện cũ hoặc trùng | Đạt ở frontend | Khi mô phỏng sự kiện cũ và trùng bằng hàm render, giao diện giữ COMPLETED version 4, không lùi về ACCEPTED version 2. |
| W3-TC10 | Bấm nhanh nhiều lần | Đạt ở frontend | Nút bị khóa khi chờ phản hồi. Lần thử đối chiếu log ghi nhận một yêu cầu updateOrderStatus tại dispatcher. Xử lý yêu cầu trùng phía backend được kiểm tra riêng tại TC02. |
| W3-TC11 | Phân quyền | Đạt trong tình huống đã thử | C002/D002 bị từ chối đọc, theo dõi và cập nhật ngoài quyền; thiếu/sai token được dispatcher ghi INVALID_SESSION. Với ORD-5795e7b8c66957d13f26e5ee, D002 không nhận broadcast trái quyền sau khi D001 nhận đơn. Log sent=2, skipped=1, gone=0; bộ đếm tổng hợp không xác định trực tiếp actor bị bỏ qua. |
| W3-TC12 | Hai tài xế tranh nhận đơn | Đạt theo kết quả TV1 | Hai yêu cầu được gửi gần đồng thời. Chỉ một tài xế nhận đơn thành công và dữ liệu cuối có một driverId. |
| W3-TC13 | Logging và quyền vận hành | Đạt trong phạm vi đã kiểm tra | Stage dev LoggingLevel INFO, DataTraceEnabled=false, Custom access logging tắt; execution log có route $default và integration status 200. API Gateway và năm Lambda tuần 3 có retention Never expire. Đã đọc/cập nhật cấu hình logging, xem log groups/events và cập nhật workflow thành công; không phải kiểm toán đầy đủ mọi quyền IAM. |

## 3. Các đơn kiểm thử phía TV2

| Mã đơn | Mục đích kiểm thử |
| --- | --- |
| `ORD-1ca0c571f442849f9b85cc16` | Tạo đơn PLACED version 1, nhận đơn và đồng bộ ACCEPTED version 2 giữa hai giao diện. |
| `ORD-7adb5028048463cb21764756` | Kiểm tra khóa nút khi đang gửi yêu cầu. |
| `ORD-746e8af0cf650b5a3c9fb195` | Kiểm tra đồng bộ trạng thái, hoàn tất đơn, execution và tải lại trang. |
| `ORD-217c2a03e405d72853e6864b` | Kiểm tra khôi phục theo dõi và nhận cập nhật sau reconnect. |
| `ORD-d709117de766c314d9e6e0ce` | Kiểm tra bấm nhận đơn liên tục và đối chiếu dispatcher log. |
| `ORD-071dc67f107f9beb266a21e4` | Kiểm tra đơn đổi trạng thái khi khách offline và khôi phục snapshot sau reconnect. |
| `ORD-5795e7b8c66957d13f26e5ee` | Kiểm tra quyền nhận broadcast sau khi đơn được phân công cho D001. |
| `ORD-6b8bc28e817c29374c544236` | Kiểm tra từ chối expectedVersion cũ và đọc lại snapshot. |
| `ORD-efa289eb56e757c8cac3bb98` | Kiểm tra khôi phục giao diện sau CONFLICT và chuyển trạng thái hợp lệ tiếp theo. |
| `ORD-381e33d0155909969f8f2d98` | Kiểm thử lưu trạng thái timeout sau sửa tại PrepareAcceptedTask. |
| `ORD-dcba07009952a36dee9e01f4` | Kiểm thử hồi quy sau cập nhật dispatcher và xác nhận execution SUCCEEDED. |

## 4. Kết quả kiểm thử bổ sung

### 4.1. Xử lý version cũ và khôi phục giao diện

Yêu cầu chuyển sang DELIVERING với expectedVersion 1 được gửi khi đơn đang ở ACCEPTED version 2. Backend trả CONFLICT. Giao diện gửi yêu cầu đọc lại đơn và hiển thị snapshot hiện tại.

Trên đơn `ORD-efa289eb56e757c8cac3bb98`, nút Bắt đầu giao được bật lại. Yêu cầu hợp lệ tiếp theo được tiếp nhận và đơn chuyển sang DELIVERING version 3. Polling đang bật trong lần thử; minh chứng chưa tách riêng tác động của polling và nhánh tải lại sau lỗi.

Minh chứng:

- [Version cũ bị từ chối](../../evidence/LeHuy/Week_03/W3-TV2-06_03_StaleVersionRejected.png).
- [Snapshot sau CONFLICT](../../evidence/LeHuy/Week_03/W3-TV2-06_04_AutoRefreshAfterConflict.png).
- [Chuyển trạng thái sau CONFLICT](../../evidence/LeHuy/Week_03/W3-TV2-06_05_TransitionAfterConflict.png).

### 4.2. Khôi phục khi đơn thay đổi trong thời gian offline

Với đơn `ORD-071dc67f107f9beb266a21e4`, khách hàng mất kết nối trong lúc tài xế nhận đơn. Sau khi kết nối lại, khách nhận snapshot ACCEPTED version 2 và tiếp tục nhận sự kiện DELIVERING version 3.

Minh chứng:

- [Khách hàng offline](../../evidence/LeHuy/Week_03/W3-TV2-03_08_CustomerOffline.png).
- [Tài xế cập nhật khi khách offline](../../evidence/LeHuy/Week_03/W3-TV2-03_09_DriverUpdatedWhileCustomerOffline.png).
- [Khôi phục snapshot sau reconnect](../../evidence/LeHuy/Week_03/W3-TV2-03_10_CatchUpAfterReconnect.png).
- [Nhận sự kiện mới sau reconnect](../../evidence/LeHuy/Week_03/W3-TV2-03_11_NewEventAfterCatchUp.png).

### 4.3. Phân quyền truy cập và cập nhật

Các yêu cầu đọc, theo dõi và cập nhật ngoài quyền bị từ chối. Kết nối thiếu token hoặc dùng token sai được dispatcher ghi nhận INVALID_SESSION.

Với đơn `ORD-5795e7b8c66957d13f26e5ee`, D002 theo dõi đơn khi đơn còn PLACED. Sau khi D001 nhận đơn, D002 không nhận cập nhật trái quyền trong khoảng thời gian quan sát. Log broadcast ghi nhận sent=2, skipped=1 và gone=0.

Minh chứng:

- [D002 cập nhật trái quyền](../../evidence/LeHuy/Week_03/W3-TV2-04_07_D002UpdateForbidden.png).
- [Dữ liệu sau yêu cầu trái quyền](../../evidence/LeHuy/Week_03/W3-TV2-04_08_OrderUnchangedAfterForbidden.png).
- [C002 cập nhật trái quyền](../../evidence/LeHuy/Week_03/W3-TV2-04_09_C002UpdateForbidden.png).
- [Thiếu token](../../evidence/LeHuy/Week_03/W3-TV2-04_10_MissingTokenRejected.png).
- [Token không hợp lệ](../../evidence/LeHuy/Week_03/W3-TV2-04_11_InvalidTokenRejected.png).
- [D002 theo dõi trước khi phân công](../../evidence/LeHuy/Week_03/W3-TV2-04_12_D002SubscribedBeforeAssignment.png).
- [D001 nhận đơn](../../evidence/LeHuy/Week_03/W3-TV2-04_13_D001Accepted.png).
- [D002 không nhận broadcast trái quyền](../../evidence/LeHuy/Week_03/W3-TV2-04_14_D002NoUnauthorizedBroadcast.png).
- [Log broadcast](../../evidence/LeHuy/Week_03/W3-TV2-04_15_BroadcastPermissionCheck.png).

### 4.4. Kiểm thử hồi quy sau cập nhật dispatcher

- **Ngày thực hiện:** 25/10/2026.
- **Mã đơn:** `ORD-dcba07009952a36dee9e01f4`.
- **Phiên kiểm thử:** C001 và D001.
- **Thao tác:** Tạo đơn, nhận đơn, bắt đầu giao và hoàn tất.
- **Trạng thái cuối:** COMPLETED.
- **Version:** 4.
- **Tài xế:** D001.
- **workflowStatus:** SUCCEEDED.
- **executionStatus:** SUCCEEDED sau khi đọc lại đơn.

Nhật ký khách hàng ghi nhận cập nhật DELIVERING và COMPLETED qua ORDER_UPDATED. Các nút chuyển trạng thái bị khóa sau hoàn tất. Lần hồi quy này diễn ra trước khi sửa PersistWorkflowFailure, không xác nhận luồng thành công đầy đủ sau bản sửa workflow.

Minh chứng:

- [Chuyển tiếp expectedVersion](../../evidence/LeHuy/Week_03/W3-TV2-01_02_ExpectedVersionForwarded.png).
- [Cấu hình broadcast](../../evidence/LeHuy/Week_03/W3-TV2-01_03_BroadcastEnvironment.png).
- [Khách hàng sau triển khai](../../evidence/LeHuy/Week_03/W3-TV2-01_04_CustomerAfterDeploy.png).
- [Tài xế sau triển khai](../../evidence/LeHuy/Week_03/W3-TV2-01_05_DriverAfterDeploy.png).

### 4.5. Logging, retention và quyền vận hành

Ngày 25/10/2026, TV2 xác nhận stage dev có LoggingLevel INFO, DataTraceEnabled=false và Custom access logging tắt. API Gateway sử dụng CloudWatch Logs role ARN `arn:aws:iam::165662523632:role/LabRole`. Execution log tại `/aws/apigateway/lob1j5l21i/dev` ghi request route `$default` và integration status `200`.

Log group API Gateway và năm Lambda prepare, submit, commit, dispatcher, broadcast có retention Never expire. Các thao tác đọc/cập nhật cấu hình logging, xem log groups/events và cập nhật workflow đã thực hiện thành công. Không kết luận về quyền sửa IAM policy vì chưa kiểm thử thao tác này.

- [Retention Lambda](../../evidence/LeHuy/Week_03/W3-TV2-05_04_LambdaLogRetention.png).
- [Retention API Gateway](../../evidence/LeHuy/Week_03/W3-TV2-05_05_ApiGatewayLogRetention.png).
- [Execution log thực tế](../../evidence/LeHuy/Week_03/W3-TV2-05_06_ApiGatewayExecutionLog.png).

Ảnh WebSocketLoggingConfigured thể hiện bước cấu hình trung gian Errors only. Giá trị cuối INFO được TV2 xác nhận qua CLI.

### 4.6. Nguyên nhân timeout và kiểm thử bản sửa

Execution cũ của `ORD-071dc67f107f9beb266a21e4` hết thời gian chờ tại PrepareCompletedTask. HandleTimeout kiểu Pass chỉ ghi TIMED_OUT vào dữ liệu execution, không cập nhật Orders nên snapshot vẫn ghi workflowStatus RUNNING. Lịch sử cũ được giữ nguyên.

Workflow TV2 tuần 3 đã đồng bộ từ `workflow-fixed-week3.json` tải từ CloudShell. HandleTimeout/HandleWorkflowError chuyển qua PersistWorkflowFailure để lưu workflowStatus và workflowEndedAt, sau đó mới chuyển WorkflowFailed. Ba bước commit có Catch States.ALL vào HandleWorkflowError; status nghiệp vụ, version và luồng broadcast được giữ nguyên.

Trên đơn mới `ORD-381e33d0155909969f8f2d98`, không nhận đơn và chờ PrepareAcceptedTask timeout 300 giây. PersistWorkflowFailure thành công; Orders lưu TIMED_OUT và workflowEndedAt, giữ status PLACED, version 1. Snapshot trên **giao diện tài xế** có workflowStatus TIMED_OUT, executionStatus FAILED, readySteps rỗng và các nút bị khóa. FAILED là kết quả của state Fail theo thiết kế, không phải PersistWorkflowFailure thất bại.

- [Workflow cũ và nhánh kết thúc](../../evidence/LeHuy/Week_03/W3-TV2-06_06_WorkflowFailureCause.png).
- [Chi tiết timeout execution cũ](../../evidence/LeHuy/Week_03/W3-TV2-06_07_CallbackTimeoutDetails.png).
- [Snapshot tài xế sau sửa](../../evidence/LeHuy/Week_03/W3-TV2-06_08_TimeoutSnapshotAfterFix.png).
- [PersistWorkflowFailure thành công](../../evidence/LeHuy/Week_03/W3-TV2-06_09_TimeoutWorkflowAfterFix.png).
- [Orders lưu timeout](../../evidence/LeHuy/Week_03/W3-TV2-06_10_TimeoutOrderPersisted.png).

## 5. Giới hạn và thông tin bàn giao

- TC06 sau sửa mới kiểm thử timeout tại PrepareAcceptedTask trên đơn mới; chưa kiểm thử riêng lỗi commit hoặc timeout tại cả ba bước chờ.
- Kết quả yêu cầu đến trễ và các ca backend khác được tổng hợp theo worklog và minh chứng TV1.
- Hồi quy đơn ORD-dcba07009952a36dee9e01f4 diễn ra trước PersistWorkflowFailure. Chưa có lần hồi quy toàn luồng thành công sau bản sửa này.
- TC03 có polling đang bật; TC09 mô phỏng xử lý render tại frontend.
- Kết luận broadcast dựa trên danh tính phiên, ảnh giao diện và log tổng hợp; sent/skipped/gone không xác định trực tiếp kết nối nào bị bỏ qua.
- C001/C002/D001/D002 là các phiên demo. Kết quả thiếu/sai token được xác nhận bằng log INVALID_SESSION; HTTP status tương ứng chưa được ghi nhận.
- Logging và quyền vận hành được kiểm tra trong phạm vi nêu tại TC13; không phải kiểm toán IAM đầy đủ.
- Chưa xác định SHA chính xác của phiên bản đã triển khai. Hồ sơ xác định phiên bản theo các tệp Week_03 và lần kiểm thử: frontend/dispatcher cho các ca ngày 24–25/10; workflow TV2 đồng bộ từ CloudShell cho ca timeout sau sửa.
- Thời gian làm việc tuần 3: chưa tổng hợp.
- Tài nguyên được giữ lại tại thời điểm kiểm thử.
- Ngày 25/10/2026, Learner Lab hiển thị Used $0 of $50 và thời gian tích lũy 18:35:00 (1115 phút). Đây là số liệu toàn lab, không phải chi phí hoặc giờ làm riêng tuần 3. Chi phí tuần 3 chưa có số liệu tách riêng. Thông tin No running instance chỉ phản ánh instance, không xác nhận Lambda, API Gateway hoặc DynamoDB đã dừng.
- [Ảnh budget toàn lab](../../evidence/LeHuy/Week_03/W3-TV2-07_01_LabBudget.png).
- [Cấu hình biến môi trường dispatcher](../../evidence/LeHuy/Week_03/W3-TV2-01_01_DispatcherEnvironment.png) đã che kín giá trị SESSION_TOKENS_JSON; phần cấu hình còn lại giữ nguyên.

## 6. Kết luận

Các ca có kết quả xác nhận luồng nghiệp vụ, realtime, reconnect, version cũ và phân quyền trong phạm vi đã thử. Sau sửa workflow, kiểm thử trên đơn mới xác nhận trạng thái timeout được lưu vào Orders trước khi execution kết thúc tại state Fail. Logging, retention và quyền vận hành đã được đối chiếu theo TC13. Phạm vi kiểm thử, thông tin bàn giao chưa xác định và các giới hạn được trình bày tại mục 5.
