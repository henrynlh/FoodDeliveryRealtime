# KẾT QUẢ KIỂM THỬ TUẦN 4

- Dự án: FoodDeliveryRealtime.
- Thời gian tổng hợp: 30/10/2026 – 01/11/2026.
- Phát: Trương Tấn Phát — MSSV 24110298.
- Huy: Nguyễn Lê Huy — MSSV 24110221.
- Region: us-east-1.
- Kế hoạch: [Phân công tuần 4](../../TaskAssignments/Week_04.md).

## 1. Môi trường kiểm thử

| Môi trường | AWS Account ID | Người thực hiện | Phạm vi |
|---|---|---|---|
| Phát | 053151184394 | Trương Tấn Phát | Backend, lỗi commit, gửi lặp, yêu cầu trễ và SNS. |
| Huy | 165662523632 | Nguyễn Lê Huy | Giao diện, WebSocket, timeout, reconnect, CONFLICT, logging và tranh nhận đơn bổ sung. |

Nhóm kiểm thử trên hai môi trường độc lập. Kết quả dưới đây được ghi theo từng tài khoản để phân biệt các lần chạy.

Ngày 01/11/2026, Huy đối chiếu bổ sung dữ liệu backend của hai đơn timeout đã kiểm thử ngày 30/10/2026. Đây không phải hai lần chạy timeout mới.

## 2. Tổng hợp kết quả

| Mã | Nội dung | Kết quả | Phạm vi xác nhận |
|---|---|---|---|
| W4-TC01 | Toàn luồng tạo, nhận, giao và hoàn tất | Đạt trong các lần thử đã ghi nhận | Giao diện do Huy phụ trách và luồng backend do Phát phụ trách được kiểm tra trên các đơn riêng. |
| W4-TC02 | Timeout tại ba bước chờ | Đạt trong phạm vi đã đối chiếu | Giao diện, execution và dữ liệu của các ca tương ứng. |
| W4-TC03 | Lỗi commit có kiểm soát | Đạt trong lần kiểm thử của Phát | Kiểm tra actor giữ claim và nhánh Catch lưu lỗi. |
| W4-TC04 | Gửi yêu cầu sau timeout | Đạt trong lần kiểm thử của Phát | Submit từ chối yêu cầu đến trễ, đơn không đổi. |
| W4-TC05 | Phục hồi sau CONFLICT khi tắt tự đọc | Đạt trong lần kiểm thử của Huy | Giao diện tự đọc lại thông tin và cho phép thao tác hợp lệ tiếp theo. |
| W4-TC06 | Reconnect và ngắt chủ động | Đạt trong tình huống mô phỏng đã ghi nhận | Khôi phục thông tin mới nhất và tiếp tục nhận cập nhật. |
| W4-TC07 | Gửi lặp và tranh nhận đơn | Đạt trong các lần thử đã ghi nhận | Gửi lặp trên môi trường của Phát, tranh nhận đơn bổ sung trên môi trường của Huy. |
| W4-TC08 | Truy vết yêu cầu qua nhật ký | Đạt trong lần kiểm thử của Huy | Đối chiếu giao diện, Dispatcher và API Gateway. |
| W4-TC09 | Kịch bản trình diễn tổng hợp | Hoàn tất theo xác nhận của nhóm | Phần trình diễn và video demo đã hoàn tất; kết quả kỹ thuật được trình bày theo từng ca bên dưới. |

## 3. W4-TC01 Toàn luồng thành công

### Giao diện và WebSocket trên môi trường của Huy

- Ngày thực hiện: 30/10/2026.
- Phiên: khách hàng C001 và tài xế D001.
- Mã đơn: `ORD-8210a2c11e7fdfe46cbae6b9`.
- Thực hiện tạo đơn, nhận đơn, bắt đầu giao và hoàn tất.

| Bước | Trạng thái | Version |
|---|---|---|
| Tạo đơn | PLACED | 1 |
| Nhận đơn | ACCEPTED | 2 |
| Bắt đầu giao | DELIVERING | 3 |
| Hoàn tất | COMPLETED | 4 |

- Hai giao diện hiển thị cùng tiến độ, tài xế D001.
- Kết quả cuối có workflowStatus SUCCEEDED.
- Sau khi đọc lại, executionStatus SUCCEEDED.
- Ba nút chuyển trạng thái bị khóa, readySteps rỗng.
- Nhật ký sau hoàn tất không tiếp tục gửi getOrder định kỳ trong khoảng đã quan sát.
- Step Functions xác nhận execution Succeeded.

Minh chứng:

- [Khách hàng hoàn tất](../../evidence/LeHuy/Week_04/W4-TV2-01_08_CustomerCompleted.png).
- [Tài xế hoàn tất](../../evidence/LeHuy/Week_04/W4-TV2-01_09_DriverCompleted.png).
- [Dừng tự đọc định kỳ](../../evidence/LeHuy/Week_04/W4-TV2-01_10_PollingStopped.png).
- [Execution thành công](../../evidence/LeHuy/Week_04/W4-TV2-01_11_ExecutionSucceeded.png).

### Backend trên môi trường của Phát

- Ngày thực hiện: 31/10/2026.
- Đơn: `ORD-W4-E2E-bc9752180dd8`.
- Orders đạt COMPLETED, version 4, driverId D001.
- Execution thành công.
- Có ba bước xử lý với committedVersion lần lượt 2, 3, 4.

Minh chứng:

- [Execution backend](../../evidence/TanPhat/Week_04/W4-TV1-03_01_SuccessExecution.png).
- [Orders hoàn tất](../../evidence/TanPhat/Week_04/W4-TV1-03_02_CompletedOrder.png).
- [Ba bước xử lý](../../evidence/TanPhat/Week_04/W4-TV1-03_03_ThreeTasksDone.png).

## 4. W4-TC02 Timeout tại ba bước chờ

Huy dùng ba đơn riêng, không thực hiện thao tác tiếp theo trong thời gian chờ 300 giây.

| Ca | Mã đơn | Status giữ lại | Version |
|---|---|---|---|
| Chờ nhận đơn | ORD-d5648ede704e795bc79ffeea | PLACED | 1 |
| Chờ bắt đầu giao | ORD-3e832b119b6cc9ebe3cecc86 | ACCEPTED | 2 |
| Chờ hoàn tất | ORD-be0dec6579d25293f355a7de | DELIVERING | 3 |

Kết quả giao diện và execution:

- workflowStatus TIMED_OUT.
- executionStatus FAILED.
- Giao diện hiển thị hết thời gian chờ.
- Ba nút chuyển trạng thái bị khóa, readySteps rỗng.
- Execution đi qua HandleTimeout, PersistWorkflowFailure và WorkflowFailed.
- Execution FAILED do workflow kết thúc bằng state Fail. Nguyên nhân được ghi nhận là TIMED_OUT.

Đối chiếu dữ liệu bổ sung ngày 01/11/2026:

- Ca chờ bắt đầu giao: Orders giữ ACCEPTED, version 2, D001, có workflowEndedAt. Task ACCEPTED đã DONE ở version 2. DELIVERING còn READY.
- Ca chờ hoàn tất: Orders giữ DELIVERING, version 3, D001, có workflowEndedAt. ACCEPTED và DELIVERING đã DONE ở version 2 và 3. COMPLETED còn READY.
- Các task chờ chưa bị ghi nhận hoàn thành.
- Task còn READY không có nghĩa callback còn hiệu lực.

Minh chứng:

- [Sơ đồ timeout chờ nhận](../../evidence/LeHuy/Week_04/W4-TV2-02_04_AcceptTimeoutGraph.png).
- [Sơ đồ timeout chờ bắt đầu giao](../../evidence/LeHuy/Week_04/W4-TV2-02_08_DeliveringTimeoutGraph.png).
- [Sơ đồ timeout chờ hoàn tất](../../evidence/LeHuy/Week_04/W4-TV2-02_12_CompletedTimeoutGraph.png).
- [Orders ca B](../../evidence/TanPhat/Week_04/W4-TV1-03_05B_TimeoutOrder.png).
- [WorkflowTasks ca B](../../evidence/TanPhat/Week_04/W4-TV1-03_06B_TimeoutTasks.png).
- [Orders ca C](../../evidence/TanPhat/Week_04/W4-TV1-03_05C_TimeoutOrder.png).
- [WorkflowTasks ca C](../../evidence/TanPhat/Week_04/W4-TV1-03_06C_TimeoutTasks.png).

Phát cũng kiểm thử riêng ca chờ nhận đơn trên tài khoản 053151184394; kết quả được ghi trong worklog của Phát.

## 5. W4-TC03 Lỗi commit có kiểm soát

- Người thực hiện: Trương Tấn Phát.
- Ngày thực hiện: 31/10/2026.
- Mã đơn: `ORD-ada768ea555f5ad27823ed4e`.
- Script: `commit_failure_probe.py`.
- Sử dụng workflow thử riêng, sao chép các state liên quan từ workflow chính.
- Task được giữ quyền bởi D001, nhưng đầu vào commit truyền actor D002.

Kết quả:

- Commit từ chối vì actor không khớp người giữ quyền.
- Catch chuyển sang xử lý lỗi và lưu kết quả vào Orders.
- Đơn giữ PLACED, version 1.
- workflowStatus FAILED, có workflowEndedAt.
- Task giữ CLAIMED của D001, chưa chuyển DONE.
- File kết quả đánh giá PASS.

Giới hạn: xác nhận kiểm tra quyền giữ claim và nhánh lưu lỗi. Không đại diện cho mọi loại lỗi giao dịch DynamoDB.

Minh chứng:

- [Commit bị từ chối](../../evidence/TanPhat/Week_04/W4-TV1-02_01_CommitRejected.png).
- [Nhánh lưu lỗi](../../evidence/TanPhat/Week_04/W4-TV1-02_02_FailurePersisted.png).
- [Kết quả tự động](../../evidence/TanPhat/Week_04/w4-commit-failure-result.json).

### Kiểm thử bổ sung trên môi trường của Huy

- Ngày thực hiện: 01/11/2026.
- Người thực hiện: Nguyễn Lê Huy.
- Tài khoản: 165662523632.
- Mã đơn: `ORD-991d39e074d74935c9506d47`.
- Script kiểm thử riêng ghi nhận PASS, execution FAILED và toàn bộ checks bằng true.
- Hai giao diện hiển thị “Luồng xử lý gặp lỗi”.
- Đơn giữ PLACED, version 1. workflowStatus và executionStatus đều FAILED.
- readySteps rỗng, ba nút tài xế bị khóa, nhật ký ghi ORDER_TERMINAL.
- Kết luận: Đạt phần hiển thị và khóa thao tác khi workflow FAILED.

Minh chứng:

- [Kết quả tự động](../../evidence/LeHuy/Week_04/W4-TV2-02_CommitFailureResult.json).
- [Tài xế](../../evidence/LeHuy/Week_04/W4-TV2-02_14_WorkflowFailedDriver.png).
- [Khách hàng](../../evidence/LeHuy/Week_04/W4-TV2-02_15_WorkflowFailedCustomer.png).

## 6. W4-TC04 Yêu cầu đến sau timeout

- Người thực hiện: Trương Tấn Phát.
- Dùng đơn đã timeout tại bước chờ nhận đơn.
- Gọi Submit với targetStatus ACCEPTED, expectedVersion 1.

Kết quả:

- Submit trả ok false, errorCode TASK_EXPIRED.
- Orders vẫn PLACED, version 1, workflowStatus TIMED_OUT.
- Không ghi nhận chuyển trạng thái nghiệp vụ sau timeout.

Minh chứng:

- [Submit trễ bị từ chối](../../evidence/TanPhat/Week_04/W4-TV1-03_07_LateSubmitRejected.png).
- [Orders không đổi](../../evidence/TanPhat/Week_04/W4-TV1-03_08_OrderUnchangedAfterLate.png).

Giới hạn: ca này kiểm tra yêu cầu qua Submit sau timeout, không phải gọi trực tiếp API SendTaskSuccess bằng token cũ.

## 7. W4-TC05 Phục hồi sau CONFLICT

- Người thực hiện: Nguyễn Lê Huy.
- Ngày thực hiện: 30/10/2026.
- Mã đơn: `ORD-d9a696060870f0c79769e62e`.
- Tắt tự đọc định kỳ.
- Mô phỏng phiên bản cũ trong bộ nhớ trình duyệt.
- Gửi DELIVERING với expectedVersion 1 khi đơn đang ACCEPTED, version 2.

Kết quả:

- Backend trả CONFLICT.
- Giao diện tự gửi getOrder qua cơ chế xử lý lỗi.
- Thông tin được khôi phục về ACCEPTED, version 2.
- Nút Bắt đầu giao được bật lại.
- Yêu cầu hợp lệ tiếp theo chuyển đơn sang DELIVERING, version 3.

Minh chứng:

- [Phục hồi khi tự đọc đang tắt](../../evidence/LeHuy/Week_04/W4-TV2-04_02_ConflictRecoveredWithoutPolling.png).
- [Thao tác hợp lệ sau phục hồi](../../evidence/LeHuy/Week_04/W4-TV2-04_03_ValidTransitionAfterConflict.png).

## 8. W4-TC06 Khôi phục kết nối

- Người thực hiện: Nguyễn Lê Huy.
- Ngày thực hiện: 30/10/2026.
- Mã đơn reconnect: `ORD-a47b376b4fde31fb9307f586`.

Kết quả:

- Ngắt chủ động: giao diện CLOSED, khóa thao tác và ghi DISCONNECTED_BY_USER.
- Trong khoảng nhật ký được ghi lại sau khi ngắt chủ động, giao diện không tự kết nối lại.
- Khi mô phỏng gián đoạn, khách hàng tự kết nối và theo dõi lại đơn.
- Tài xế cập nhật khi khách hàng đang ngắt kết nối.
- Khi kết nối trở lại, khách hàng tự lấy trạng thái DELIVERING, version 3.
- Sau đó tiếp tục nhận cập nhật COMPLETED, version 4.

Minh chứng:

- [Ngắt chủ động](../../evidence/LeHuy/Week_04/W4-TV2-03_01_ManualDisconnect.png).
- [Khôi phục thông tin mới nhất](../../evidence/LeHuy/Week_04/W4-TV2-03_04_CustomerRestoredLatestSnapshot.png).
- [Tiếp tục nhận cập nhật](../../evidence/LeHuy/Week_04/W4-TV2-03_05_RealtimeAfterReconnect.png).

Giới hạn: sử dụng đóng WebSocket và sự kiện offline/online mô phỏng, không ngắt mạng vật lý.

## 9. W4-TC07 Gửi lặp và tranh nhận đơn

### Gửi lặp trên môi trường của Phát

- Người thực hiện: Trương Tấn Phát.
- Đơn: `ORD-W4-DUP-e3c52e56fa72`.
- Lần gửi đầu được tiếp nhận và đơn chuyển sang ACCEPTED, version 2.
- Gửi lại cùng actor và requestId trả ALREADY_DONE.
- Version không tăng thêm.
- Commit lặp trả duplicate true, sns SKIPPED_DUPLICATE.

Minh chứng:

- [Submit lặp](../../evidence/TanPhat/Week_04/W4-TV1-04_02_DuplicateSubmit.png).
- [Version không tăng thêm](../../evidence/TanPhat/Week_04/W4-TV1-04_03_DuplicateOrderUnchanged.png).
- [Commit lặp](../../evidence/TanPhat/Week_04/W4-TV1-04_04_DuplicateCommit.png).

### Tranh nhận đơn bổ sung trên môi trường của Huy

- Người thực hiện: Nguyễn Lê Huy.
- Ngày thực hiện: 01/11/2026, giờ Việt Nam.
- Mã đơn: `ORD-87610c608da45f2e46989b4a`.
- Dùng race_accept.py gửi hai yêu cầu nhận đơn từ D001 và D002 với expectedVersion 1.

Kết quả:

- D001 bị CONFLICT.
- D002 được tiếp nhận với QUEUED.
- Orders xác nhận ACCEPTED, version 2, driverId D002.
- Task ACCEPTED xác nhận DONE, actorId D002, committedVersion 2.
- Đơn sau đó timeout ở bước chờ bắt đầu giao, nhưng vẫn giữ ACCEPTED, version 2.
- Kết luận: chỉ D002 nhận được đơn trong lần thử này.

Minh chứng:

- [Phản hồi D001](../../evidence/TanPhat/Week_04/W4-TV1-04_05_RaceRequestsResponses.png).
- [Phản hồi D002](../../evidence/TanPhat/Week_04/W4-TV1-04_06_RaceD002Response.png).
- [Orders cuối](../../evidence/TanPhat/Week_04/W4-TV1-04_07_RaceOrderFinal.png).
- [Task nhận đơn](../../evidence/TanPhat/Week_04/W4-TV1-04_08_RaceTaskFinal.png).
- [Yêu cầu và phản hồi](../../evidence/TanPhat/Week_04/W4-TV1-04_RaceRequestsResponses.json).

## 10. W4-TC08 Truy vết yêu cầu qua nhật ký

- Người thực hiện: Nguyễn Lê Huy.
- Ngày thực hiện: 30/10/2026.
- Mã đơn: `ORD-d9a696060870f0c79769e62e`.
- RequestId: `224011af-658c-43d0-9f56-f96325d04fc6`.

Kết quả:

- Dispatcher ghi nhận updateOrderStatus, D001, kết quả CONFLICT.
- lambdaRequestId được đối chiếu với integration request ID tại API Gateway.
- API Gateway ghi nhận route $default, response status 200.
- Mã 200 không có nghĩa thao tác nghiệp vụ đã được chấp nhận. Kết quả nghiệp vụ của yêu cầu vẫn là CONFLICT.
- Lần chuyển trạng thái hợp lệ sau đó có log broadcast DELIVERING, version 3, sent 2.

Minh chứng:

- [Dispatcher](../../evidence/LeHuy/Week_04/W4-TV2-05_01_DispatcherConflictLog.png).
- [Integration request ID](../../evidence/LeHuy/Week_04/W4-TV2-05_02_ApiGatewayExecutionLog.png).
- [Route và response](../../evidence/LeHuy/Week_04/W4-TV2-05_03_ApiGatewayRouteAndStatus.png).
- [Broadcast](../../evidence/LeHuy/Week_04/W4-TV2-05_04_BroadcastLog.png).

## 11. Đối chiếu SNS

- Phát đã đối chiếu subscription, kết quả PUBLISHED tại các mốc ACCEPTED và COMPLETED, cùng minh chứng email.
- Ảnh email trong bộ minh chứng thể hiện thông báo COMPLETED của đơn E2E.
- Commit lặp ghi SKIPPED_DUPLICATE.
- Không suy ra cơ chế giao thông báo luôn đúng một lần từ các minh chứng này.
- Trên tài khoản của Huy, bộ ảnh kiểm kê ngày 01/11/2026 mới xác nhận topic tồn tại. Chưa dùng ảnh kiểm kê để kết luận email đã được nhận.

Minh chứng:

- [Subscription của Phát](../../evidence/TanPhat/Week_04/W4-TV1-05_01_SnsSubscription.png).
- [Publish khi nhận đơn](../../evidence/TanPhat/Week_04/W4-TV1-05_02_AcceptedPublish.png).
- [Publish khi hoàn tất](../../evidence/TanPhat/Week_04/W4-TV1-05_03_CompletedPublish.png).
- [Email thực tế](../../evidence/TanPhat/Week_04/W4-TV1-05_04_NotificationEmail.png).

## 12. Tài liệu liên quan

- [Worklog của Phát](../../worklog/TanPhat/Week_04.md).
- [Worklog của Huy](../../worklog/LeHuy/Week_04.md).
- [Bàn giao backend](../../design/Week_04/TV1_backend_handoff.md).
- [Kiểm kê tài nguyên](../../design/Week_04/resource_inventory.md).
