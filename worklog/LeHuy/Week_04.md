### W4-TV2-01 — Cập nhật giao diện và kiểm thử hồi quy toàn luồng

- Ngày thực hiện: 30/10/2026.
- Người thực hiện: Nguyễn Lê Huy — TV2 — 24110221.
- Môi trường: AWS us-east-1, WebSocket stage dev.
- Phiên kiểm thử: khách hàng C001 và tài xế D001.
- Mã đơn: `ORD-8210a2c11e7fdfe46cbae6b9`.
- Mã kiểm thử liên quan: W4-TC01.

#### Nội dung thực hiện

- Chuẩn bị ba file `customer.html`, `driver.html`, `shared.js`
  trong `code/LeHuy/Week_04/frontend/`.
- Cập nhật tiêu đề giao diện sang tuần 4.
- Bổ sung hiển thị trạng thái kết thúc của workflow.
- Khóa các nút chuyển trạng thái và dừng đọc đơn định kỳ
  khi đơn đã kết thúc.
- Giữ cơ chế đọc lại snapshot sau yêu cầu chuyển trạng thái.
- Kết nối hai giao diện, kiểm tra Ping và thực hiện luồng tạo đơn, nhận đơn, bắt đầu giao, hoàn tất.
- Đối chiếu kết quả giao diện với execution trên Step Functions.
#### Kết quả thực tế

| Bước | Trạng thái đơn | Version | Kết quả quan sát |
|---|---|---|---|
| Tạo đơn | PLACED | 1 | Tài xế có readySteps ACCEPTED, chỉ nút Nhận đơn được bật. |
| Nhận đơn | ACCEPTED | 2 | Hai giao diện đồng bộ, driverId D001. |
| Bắt đầu giao | DELIVERING | 3 | Hai giao diện đồng bộ, tài xế có thể chọn Hoàn tất. |
| Hoàn tất | COMPLETED | 4 | workflowStatus SUCCEEDED, readySteps rỗng, ba nút chuyển trạng thái bị khóa. |

- Snapshot tài xế sau khi đọc lại ghi nhận
  `executionStatus=SUCCEEDED`.
- Khi ô tự đọc vẫn được chọn, nhật ký trong khoảng
  05:04:42–05:06:06 UTC chỉ ghi nhận ping/pong,
  không xuất hiện yêu cầu getOrder tự động.
- Step Functions xác nhận execution Succeeded.
- Execution bắt đầu lúc 11:57:28 và kết thúc lúc 12:02:31
  ngày 30/10/2026, múi giờ UTC+07:00.
  Đây là thời gian execution, không phải tổng thời gian làm việc.
- Sơ đồ execution có bước PersistWorkflowFailure.
  Luồng thành công đi qua ba bước commit và ba bước broadcast
  tới OrderCompletedSucceed.
- Kết luận: Đạt W4-TC01 trong lần kiểm thử đã ghi nhận.
  Các trường hợp timeout, lỗi commit, reconnect và CONFLICT
  được kiểm thử riêng.

#### Minh chứng

| Nội dung | Minh chứng |
|---|---|
| Kết nối khách hàng | [CustomerConnected](../../evidence/LeHuy/Week_04/W4-TV2-01_01_CustomerConnected.png) |
| Kết nối tài xế | [DriverConnected](../../evidence/LeHuy/Week_04/W4-TV2-01_02_DriverConnected.png) |
| Sẵn sàng nhận đơn | [DriverReadyToAccept](../../evidence/LeHuy/Week_04/W4-TV2-01_03_DriverReadyToAccept.png) |
| Khách hàng sau nhận đơn | [CustomerAccepted](../../evidence/LeHuy/Week_04/W4-TV2-01_04_CustomerAccepted.png) |
| Tài xế sau nhận đơn | [DriverAccepted](../../evidence/LeHuy/Week_04/W4-TV2-01_05_DriverAccepted.png) |
| Khách hàng khi đang giao | [CustomerDelivering](../../evidence/LeHuy/Week_04/W4-TV2-01_06_CustomerDelivering.png) |
| Tài xế khi đang giao | [DriverDelivering](../../evidence/LeHuy/Week_04/W4-TV2-01_07_DriverDelivering.png) |
| Khách hàng sau hoàn tất | [CustomerCompleted](../../evidence/LeHuy/Week_04/W4-TV2-01_08_CustomerCompleted.png) |
| Tài xế sau hoàn tất | [DriverCompleted](../../evidence/LeHuy/Week_04/W4-TV2-01_09_DriverCompleted.png) |
| Dừng đọc đơn định kỳ | [PollingStopped](../../evidence/LeHuy/Week_04/W4-TV2-01_10_PollingStopped.png) |
| Execution thành công | [ExecutionSucceeded](../../evidence/LeHuy/Week_04/W4-TV2-01_11_ExecutionSucceeded.png) |
| Sơ đồ execution | [ExecutionGraph](../../evidence/LeHuy/Week_04/W4-TV2-01_12_ExecutionGraph.png) |

### W4-TV2-02 — Kiểm thử giao diện khi timeout tại ba bước chờ

- Ngày thực hiện: 30/10/2026.
- Người thực hiện: Nguyễn Lê Huy — TV2 — 24110221.
- Môi trường: AWS us-east-1, WebSocket stage dev.
- Phiên kiểm thử: khách hàng C001 và tài xế D001.
- Mã kiểm thử liên quan: W4-TC02.

#### Nội dung thực hiện

- Tạo ba đơn riêng để kiểm thử timeout tại từng bước chờ.
- Giữ chức năng tự đọc đơn trên trang tài xế được bật.
- Không thực hiện thao tác tiếp theo trong thời hạn chờ 300 giây.
- Kiểm tra trạng thái, version, thông báo và các nút trên giao diện.
- Bấm Đọc đơn trên trang khách hàng để lấy snapshot sau timeout.
- Đối chiếu từng mã đơn với execution và sơ đồ Step Functions.

#### Kết quả thực tế

| Trường hợp | Mã đơn | Trạng thái sau timeout | Version | Tài xế |
|---|---|---|---|---|
| Chờ nhận đơn | ORD-d5648ede704e795bc79ffeea | PLACED | 1 | Chưa có |
| Chờ bắt đầu giao | ORD-3e832b119b6cc9ebe3cecc86 | ACCEPTED | 2 | D001 |
| Chờ hoàn tất | ORD-be0dec6579d25293f355a7de | DELIVERING | 3 | D001 |

Cả ba trường hợp đều ghi nhận:

- Hai giao diện hiển thị `workflowStatus=TIMED_OUT` và thông báo “Hết thời gian chờ xử lý”.
- Snapshot có `executionStatus=FAILED` và `readySteps=[]`.
- Trạng thái nghiệp vụ và version giữ nguyên tại bước trước timeout.
- Ba nút Nhận đơn, Bắt đầu giao và Hoàn tất trên trang tài xế bị khóa.
- Nhật ký tài xế ghi nhận ORDER_TERMINAL.
- Execution đi từ bước chờ tương ứng qua HandleTimeout, PersistWorkflowFailure và WorkflowFailed.
- PersistWorkflowFailure chạy thành công.
- Execution kết thúc Failed do nhánh timeout sử dụng state Fail. Kết quả này phù hợp với workflowStatus TIMED_OUT trong Orders.

Kết luận: Đạt W4-TC02 trong phạm vi kiểm tra giao diện, snapshot và execution tại ba bước chờ. Kiểm thử callback đến trễ và trạng thái bản ghi WorkflowTasks được đối chiếu riêng.

#### Minh chứng

| Trường hợp | Tài xế | Khách hàng | Execution | Sơ đồ |
|---|---|---|---|---|
| Chờ nhận đơn | [Ảnh 01](../../evidence/LeHuy/Week_04/W4-TV2-02_01_AcceptTimeoutDriver.png) | [Ảnh 02](../../evidence/LeHuy/Week_04/W4-TV2-02_02_AcceptTimeoutCustomer.png) | [Ảnh 03](../../evidence/LeHuy/Week_04/W4-TV2-02_03_AcceptTimeoutExecution.png) | [Ảnh 04](../../evidence/LeHuy/Week_04/W4-TV2-02_04_AcceptTimeoutGraph.png) |
| Chờ bắt đầu giao | [Ảnh 05](../../evidence/LeHuy/Week_04/W4-TV2-02_05_DeliveringTimeoutDriver.png) | [Ảnh 06](../../evidence/LeHuy/Week_04/W4-TV2-02_06_DeliveringTimeoutCustomer.png) | [Ảnh 07](../../evidence/LeHuy/Week_04/W4-TV2-02_07_DeliveringTimeoutExecution.png) | [Ảnh 08](../../evidence/LeHuy/Week_04/W4-TV2-02_08_DeliveringTimeoutGraph.png) |
| Chờ hoàn tất | [Ảnh 09](../../evidence/LeHuy/Week_04/W4-TV2-02_09_CompletedTimeoutDriver.png) | [Ảnh 10](../../evidence/LeHuy/Week_04/W4-TV2-02_10_CompletedTimeoutCustomer.png) | [Ảnh 11](../../evidence/LeHuy/Week_04/W4-TV2-02_11_CompletedTimeoutExecution.png) | [Ảnh 12](../../evidence/LeHuy/Week_04/W4-TV2-02_12_CompletedTimeoutGraph.png) |

### W4-TV2-03 — Kiểm thử ngắt chủ động và khôi phục kết nối

- Ngày thực hiện: 30/10/2026.
- Người thực hiện: Nguyễn Lê Huy — TV2 — 24110221.
- Mã kiểm thử liên quan: W4-TC06.
- Phiên kiểm thử: C001 và D001.
- Mã đơn kiểm thử reconnect: `ORD-a47b376b4fde31fb9307f586`.

#### Nội dung và kết quả

1. Ngắt kết nối chủ động trên trang tài xế.
   Giao diện chuyển CLOSED, khóa các nút cần kết nối và ghi
   DISCONNECTED_BY_USER. Ảnh ghi nhận không có lần reconnect
   tiếp theo trong phần nhật ký hiển thị.

2. Mô phỏng gián đoạn WebSocket bằng ws.close().
   Trang khách hàng tự reconnect, đăng ký theo dõi lại và
   khôi phục snapshot PLACED version 1. Sau đó nhận
   ORDER_UPDATED với ACCEPTED version 2.

3. Mô phỏng offline/online bằng sự kiện trên trình duyệt.
   Khi khách hàng đang ngắt kết nối, tài xế chuyển đơn sang
   DELIVERING version 3. Sau khi nhận sự kiện online,
   khách hàng tự reconnect và subscribeOrder, khôi phục
   snapshot DELIVERING version 3.

4. Sau reconnect, tài xế hoàn tất đơn.
   Khách hàng nhận ORDER_UPDATED và tự hiển thị
   COMPLETED version 4, workflowStatus SUCCEEDED,
   driverId D001.

#### Các mốc đối chiếu

- 05:55:04 UTC: khách hàng ghi nhận OFFLINE.
- 05:55:51 UTC: nhận sự kiện online và lên lịch reconnect.
- 05:55:54 UTC: khôi phục snapshot DELIVERING version 3.
- 05:57:21 UTC: nhận ORDER_UPDATED với COMPLETED version 4.

#### Kết luận

Đạt phần reconnect, đăng ký theo dõi lại, khôi phục snapshot
và tiếp tục nhận cập nhật realtime trong tình huống mô phỏng.
Lần thử sử dụng sự kiện offline/online và đóng WebSocket,
không phải ngắt mạng vật lý của thiết bị.

#### Minh chứng

- [Ngắt chủ động](../../evidence/LeHuy/Week_04/W4-TV2-03_01_ManualDisconnect.png).
- [Tự reconnect](../../evidence/LeHuy/Week_04/W4-TV2-03_02_CustomerReconnected.png).
- [Tài xế cập nhật khi khách ngắt kết nối](../../evidence/LeHuy/Week_04/W4-TV2-03_03_DriverChangedWhileCustomerOffline.png).
- [Khôi phục snapshot mới nhất](../../evidence/LeHuy/Week_04/W4-TV2-03_04_CustomerRestoredLatestSnapshot.png).
- [Nhận realtime sau reconnect](../../evidence/LeHuy/Week_04/W4-TV2-03_05_RealtimeAfterReconnect.png).

### W4-TV2-04 — Khôi phục sau CONFLICT khi tắt polling

- Ngày thực hiện: 30/10/2026.
- Người thực hiện: Nguyễn Lê Huy — TV2 — 24110221.
- Mã kiểm thử liên quan: W4-TC05.
- Phiên kiểm thử: khách hàng C001 và tài xế D001.
- Mã đơn: `ORD-d9a696060870f0c79769e62e`.

#### Nội dung thực hiện

- Tạo đơn mới và cho tài xế D001 nhận đơn.
- Tắt chức năng tự đọc đơn định kỳ.
- Đọc snapshot xác nhận ACCEPTED, version 2,
  readySteps có DELIVERING.
- Mô phỏng version cũ trong bộ nhớ giao diện bằng Console,
  sau đó gọi hàm transition để gửi yêu cầu DELIVERING
  với expectedVersion 1.
- Không bấm Đọc đơn trong lúc kiểm tra xử lý lỗi.
- Sau khi giao diện khôi phục snapshot, gửi lại thao tác
  bằng nút Bắt đầu giao với version hợp lệ.

#### Kết quả thực tế

- Backend từ chối yêu cầu version cũ với mã CONFLICT.
- Giao diện ghi CONFLICT_RECOVERY và tự gửi getOrder,
  dù polling đang tắt.
- Snapshot khôi phục về ACCEPTED, version 2,
  driverId D001 và readySteps DELIVERING.
- Nút Bắt đầu giao được bật lại.
- Yêu cầu hợp lệ tiếp theo dùng expectedVersion 2.
- Backend trả QUEUED, sau đó giao diện nhận ORDER_UPDATED
  với DELIVERING, version 3.
- Ô tự đọc đơn vẫn không được chọn trong suốt lần kiểm thử.

#### Kết luận

Đạt W4-TC05 trong lần kiểm thử đã ghi nhận.
Cơ chế tải lại snapshot sau CONFLICT hoạt động độc lập
với polling và cho phép tiếp tục thao tác hợp lệ.

Version cũ được mô phỏng trong bộ nhớ trình duyệt.
Không chỉnh sửa trực tiếp dữ liệu DynamoDB.

#### Minh chứng

- [Tắt polling và chuẩn bị đơn](../../evidence/LeHuy/Week_04/W4-TV2-04_01_PollingDisabled.png).
- [Khôi phục sau CONFLICT](../../evidence/LeHuy/Week_04/W4-TV2-04_02_ConflictRecoveredWithoutPolling.png).
- [Chuyển trạng thái hợp lệ sau lỗi](../../evidence/LeHuy/Week_04/W4-TV2-04_03_ValidTransitionAfterConflict.png).

### W4-TV2-05 — Đối chiếu log WebSocket và kết quả nghiệp vụ

- Ngày thực hiện: 30/10/2026.
- Người thực hiện: Nguyễn Lê Huy — TV2 — 24110221.
- Mã kiểm thử liên quan: W4-TC08.
- Mã đơn: `ORD-d9a696060870f0c79769e62e`.
- RequestId của yêu cầu version cũ:
  `224011af-658c-43d0-9f56-f96325d04fc6`.

#### Nội dung thực hiện

- Tìm log dispatcher bằng requestId của yêu cầu bị CONFLICT.
- Dùng lambdaRequestId trong log dispatcher để tìm
  AWS Integration Endpoint RequestId tương ứng tại API Gateway.
- Lọc theo mã yêu cầu API Gateway để xem route và response status.
- Tìm log broadcast bằng orderId và đối chiếu trạng thái,
  version, thời điểm với nhật ký giao diện.

#### Kết quả thực tế

- Dispatcher ghi nhận action updateOrderStatus,
  actorId D001, role DRIVER, outcome ERROR và code CONFLICT.
- Trường delivered=true ghi nhận phản hồi đã được gửi
  thành công tới kết nối.
- API Gateway ghi nhận cùng lần gọi qua route $default,
  có integration request ID trùng lambdaRequestId của dispatcher
  và response status 200.
- Status 200 của API Gateway phản ánh việc xử lý tích hợp.
  Kết quả nghiệp vụ của yêu cầu này vẫn là CONFLICT.
- Lần chuyển trạng thái hợp lệ tiếp theo được broadcast
  lúc 06:05:47 UTC với DELIVERING, version 3.
- Log broadcast ghi outcome SUCCESS, code BROADCAST_FINISHED,
  sent=2, skipped=0, gone=0.
- Trong cùng khoảng thời gian truy vấn còn có log broadcast
  COMPLETED, version 4.

#### Kết luận

Đạt W4-TC08 trong phạm vi truy vết đã kiểm tra.
Đã liên kết yêu cầu lỗi giữa giao diện, dispatcher và
API Gateway bằng các mã yêu cầu. Lần chuyển trạng thái
hợp lệ được đối chiếu với broadcast bằng orderId,
trạng thái, version và thời gian.

Bộ đếm sent phản ánh số lần gửi thành công trong lần gọi
broadcast, không tự chứng minh từng người dùng đã xem
hoặc thông báo luôn được giao đúng một lần.

#### Minh chứng

- [Dispatcher trả CONFLICT](../../evidence/LeHuy/Week_04/W4-TV2-05_01_DispatcherConflictLog.png).
- [Liên kết integration request ID](../../evidence/LeHuy/Week_04/W4-TV2-05_02_ApiGatewayExecutionLog.png).
- [Route và response status](../../evidence/LeHuy/Week_04/W4-TV2-05_03_ApiGatewayRouteAndStatus.png).
- [Kết quả broadcast](../../evidence/LeHuy/Week_04/W4-TV2-05_04_BroadcastLog.png).