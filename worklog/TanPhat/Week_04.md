# NHẬT KÝ LÀM VIỆC TUẦN 4 – TRƯƠNG TẤN PHÁT

- MSSV: 24110298.
- Thời gian: 26/10/2026 – 01/11/2026.

Trong tuần 4, Phát rà soát workflow và bổ sung bước lưu trạng thái lỗi vào Orders. Sau cập nhật, Phát kiểm thử luồng thành công, lỗi commit, timeout, yêu cầu đến trễ và gửi lặp; đồng thời đối chiếu thông báo SNS để hoàn thiện phần bàn giao backend.

## W4-TV1-01 — Chốt định nghĩa workflow và cấu hình backend

- Ngày thực hiện: 31/10/2026.
- Người thực hiện: Trương Tấn Phát — MSSV 24110298.
- Môi trường: AWS us-east-1, Account ID: 053151184394, Role: LabRole.
- Mã kiểm thử liên quan: W4-TV1-01.

### Nội dung thực hiện

- Khi rà soát workflow trên tài khoản của Phát, Phát phát hiện nhánh timeout và nhánh lỗi mới ghi kết quả trong execution qua state Pass, chưa cập nhật bảng Orders.
- Phát bổ sung `PersistWorkflowFailure`, sử dụng DynamoDB UpdateItem để lưu `workflowStatus` và `workflowEndedAt` vào Orders.
- Cập nhật định nghĩa ASL của state machine `fooddelivery-order-workflow` trên Step Functions.
- Rà soát lại cấu hình 3 Lambda backend: `fooddelivery-prepare-task`, `fooddelivery-submit-transition`, `fooddelivery-commit-transition`.
- Đợt rà soát tập trung vào việc lưu trạng thái kết thúc của workflow và kiểm tra lại cấu hình backend phục vụ trình diễn.

### Kết quả thực tế

- State machine lưu thành công, sơ đồ Graph hiển thị đủ các state `PersistWorkflowFailure`, `HandleTimeout`, `HandleWorkflowError`.
- Các state Prepare đều có `TimeoutSeconds: 300` và dùng `waitForTaskToken`.
- Ba state Commit đều có Catch bắt `States.ALL` chuyển sang xử lý lỗi.
- Ba Lambda chạy Python 3.12/3.13, memory 128 MB, timeout 30 giây và sử dụng role `LabRole`. Các thao tác DynamoDB và Step Functions trong những ca kiểm thử đã thực hiện thành công.

### Minh chứng

| Nội dung | Minh chứng |
|---|---|
| Sơ đồ và định nghĩa Workflow | [WorkflowDefinition](../../evidence/TanPhat/Week_04/W4-TV1-01_01_WorkflowDefinition.png) |
| Cấu hình Lambda backend | [BackendConfiguration](../../evidence/TanPhat/Week_04/W4-TV1-01_02_BackendConfiguration.png) |

---

## W4-TV1-02 — Kiểm thử riêng nhánh lỗi commit

- Ngày thực hiện: 31/10/2026.
- Người thực hiện: Trương Tấn Phát — MSSV 24110298.
- Mã kiểm thử liên quan: W4-TC03.
- Mã đơn kiểm thử: `ORD-ada768ea555f5ad27823ed4e`.
- State machine thử nghiệm: `fooddelivery-w4-commit-failure-43a0cba91775`.

### Nội dung thực hiện

- Tạo một state machine thử riêng bằng script `commit_failure_probe.py` để không làm ảnh hưởng đến workflow chính đang chạy.
- Tạo sẵn một đơn hàng ở trạng thái `PLACED v1` trong bảng Orders và một task `ACCEPTED` ở trạng thái `CLAIMED` do tài xế `D001` giữ quyền.
- Kích hoạt execution với payload callback có `actorId: D002` để kiểm tra khả năng từ chối yêu cầu sai actor của Lambda Commit.
- Đối chiếu execution trên Step Functions với hai bảng DynamoDB để kiểm tra yêu cầu sai actor có làm thay đổi dữ liệu hay không.

### Kết quả thực tế

- Lambda Commit phát hiện sai actor giữ claim nên ném lỗi: `ValueError: Task is not CLAIMED by this actor and request.` (tại dòng 137).
- Catch bắt được lỗi và chuyển execution qua `HandleWorkflowError`, sau đó `PersistWorkflowFailure` lưu kết quả thành công trước khi kết thúc tại `WorkflowFailed`.
- Bảng `fooddelivery-orders` giữ nguyên `status=PLACED` và `version=1`; `workflowStatus` được cập nhật thành `FAILED`, đồng thời ghi nhận `workflowEndedAt`.
- Mở bảng `fooddelivery-workflow-tasks`: Task `ACCEPTED` vẫn giữ nguyên `CLAIMED` của tài xế `D001`, không bị commit sang `DONE`.
- File JSON kết quả `w4-commit-failure-result.json` ghi nhận `evaluation=PASS`.

### Minh chứng

| Nội dung | Minh chứng |
|---|---|
| Lỗi Commit bị từ chối | [CommitRejected](../../evidence/TanPhat/Week_04/W4-TV1-02_01_CommitRejected.png) |
| Sơ đồ Catch lỗi và Persist | [FailurePersisted](../../evidence/TanPhat/Week_04/W4-TV1-02_02_FailurePersisted.png) |
| Đơn hàng sau khi lỗi | [OrderAfterFailure](../../evidence/TanPhat/Week_04/W4-TV1-02_03_OrderAfterFailure.png) |
| Task giữ CLAIMED sau lỗi | [TaskNotCommitted](../../evidence/TanPhat/Week_04/W4-TV1-02_04_TaskNotCommitted.png) |
| File kết quả tự động | [commit-result.json](../../evidence/TanPhat/Week_04/w4-commit-failure-result.json) |

---

## W4-TV1-03 — Luồng thành công E2E, Timeout 300s và Submit trễ

- Ngày thực hiện: 31/10/2026.
- Người thực hiện: Trương Tấn Phát — MSSV 24110298.
- Mã kiểm thử liên quan: W4-TC01, W4-TC02, W4-TC04.

### 1. Luồng thành công E2E (W4-TC01)

- Chạy script `run_e2e_order.py` để tạo đơn `ORD-W4-E2E-...` và gọi Submit chuyển lần lượt qua 3 bước: nhận đơn (`ACCEPTED`), bắt đầu giao (`DELIVERING`), hoàn tất (`COMPLETED`).
- Kết quả:
  - Step Functions execution chạy hết toàn bộ các bước và kết thúc với trạng thái `Succeeded`.
  - Bảng `fooddelivery-orders`: Đơn đạt `COMPLETED`, version tăng từ 1 lên 4, `driverId: D001`, `workflowStatus: SUCCEEDED`.
  - Bảng `fooddelivery-workflow-tasks`: Cả 3 task `ACCEPTED`, `DELIVERING`, `COMPLETED` đều chuyển sang `DONE`, `committedVersion` lần lượt là 2, 3, 4 và thuộc tính `taskToken` đã được xóa.

### 2. Timeout 300 giây tại bước chờ nhận đơn (W4-TC02 - Ca A)

- Chạy script `create_timeout_order.py` chọn ca 1 để tạo đơn mới ở `PLACED v1` và khởi chạy execution.
- Không gửi yêu cầu nhận đơn trong thời hạn chờ 300 giây.
- Kết quả:
  - `PrepareAcceptedTask` hết thời hạn chờ 300 giây và kích hoạt nhánh Catch `States.Timeout`.
  - Execution đi qua `HandleTimeout`, thực hiện thành công `PersistWorkflowFailure` rồi kết thúc tại `WorkflowFailed`.
  - Bảng `fooddelivery-orders`: Giữ nguyên `status=PLACED` và `version=1`, cập nhật `workflowStatus=TIMED_OUT` và `workflowEndedAt`.
  - Bảng `fooddelivery-workflow-tasks`: Task `ACCEPTED` hết hạn.

### 3. Gọi Submit sau khi workflow đã timeout (W4-TC04)

- Phát dùng mã đơn vừa timeout để gọi thử `fooddelivery-submit-transition` với `targetStatus: ACCEPTED` và `expectedVersion: 1`.
- Kết quả:
  - Lambda Submit kiểm tra thấy task đã hết hạn, trả về `ok: false`, báo lỗi `TASK_EXPIRED`.
  - Mở lại DynamoDB bảng `Orders`: Trạng thái vẫn là `PLACED`, version vẫn là 1, `workflowStatus` vẫn là `TIMED_OUT`, không bị thay đổi gì.

### Minh chứng

| Nội dung | Minh chứng |
|---|---|
| Execution E2E thành công | [SuccessExecution](../../evidence/TanPhat/Week_04/W4-TV1-03_01_SuccessExecution.png) |
| Đơn hàng COMPLETED v4 | [CompletedOrder](../../evidence/TanPhat/Week_04/W4-TV1-03_02_CompletedOrder.png) |
| Ba task DONE, đã xóa token | [ThreeTasksDone](../../evidence/TanPhat/Week_04/W4-TV1-03_03_ThreeTasksDone.png) |
| Sơ đồ execution khi Timeout 300s | [TimeoutExecution](../../evidence/TanPhat/Week_04/W4-TV1-03_04A_TimeoutExecution.png) |
| Bảng Orders ghi nhận TIMED_OUT | [TimeoutOrder](../../evidence/TanPhat/Week_04/W4-TV1-03_05A_TimeoutOrder.png) |
| Bảng Task hết hạn chờ | [TimeoutTasks](../../evidence/TanPhat/Week_04/W4-TV1-03_06A_TimeoutTasks.png) |
| Lambda Submit từ chối gọi trễ | [LateSubmitRejected](../../evidence/TanPhat/Week_04/W4-TV1-03_07_LateSubmitRejected.png) |
| Đơn không đổi sau khi gọi trễ | [OrderUnchangedAfterLate](../../evidence/TanPhat/Week_04/W4-TV1-03_08_OrderUnchangedAfterLate.png) |

---

## W4-TV1-04 — Kiểm thử gửi lặp yêu cầu (Idempotency)

- Ngày thực hiện: 31/10/2026.
- Người thực hiện: Trương Tấn Phát — MSSV 24110298.
- Mã kiểm thử liên quan: W4-TC07.

### Nội dung thực hiện

- Chạy script `create_placed_order.py` để tạo một đơn mới `ORD-W4-DUP-...` đang ở `PLACED v1`.
- Phát gọi `fooddelivery-submit-transition` với `requestId: W4-DUP-ACCEPTED-01` và `expectedVersion: 1` để gửi yêu cầu nhận đơn lần đầu.
- Sau khi workflow cập nhật xong, Phát gửi lại nguyên yêu cầu với cùng `requestId` và `expectedVersion`.
- Đối chiếu version trong DynamoDB sau hai lần gửi.
- Gọi trực tiếp `fooddelivery-commit-transition` với cùng `requestId` để kiểm tra cách xử lý yêu cầu đã commit.

### Kết quả thực tế

- Lần 1: Lambda Submit trả về `ok: true`, `status: QUEUED`. Sau đó đơn chuyển thành `ACCEPTED v2`.
- Lần 2: Giữ nguyên request gửi lại, Lambda Submit phát hiện task này đã được xử lý xong bởi đúng actor và request này, nên trả về `ok: true`, `status: ALREADY_DONE`.
- Bảng `fooddelivery-orders` vẫn ghi nhận version 2 sau lần gửi lặp.
- Gọi test trực tiếp vào Lambda Commit: Trả về `duplicate: true`, `status: COMMITTED`, `sns: SKIPPED_DUPLICATE` (bỏ qua không gửi SNS lần 2).

### Minh chứng

| Nội dung | Minh chứng |
|---|---|
| Submit lần 1 trả QUEUED | [FirstSubmit](../../evidence/TanPhat/Week_04/W4-TV1-04_01_FirstSubmit.png) |
| Submit lần 2 trả ALREADY_DONE | [DuplicateSubmit](../../evidence/TanPhat/Week_04/W4-TV1-04_02_DuplicateSubmit.png) |
| Đơn giữ version 2 không bị tăng | [DuplicateOrderUnchanged](../../evidence/TanPhat/Week_04/W4-TV1-04_03_DuplicateOrderUnchanged.png) |
| Commit bỏ qua trùng lặp | [DuplicateCommit](../../evidence/TanPhat/Week_04/W4-TV1-04_04_DuplicateCommit.png) |

---

## W4-TV1-05 — Đối chiếu thông báo Amazon SNS

- Ngày thực hiện: 31/10/2026.
- Người thực hiện: Trương Tấn Phát — MSSV 24110298.
- Mã kiểm thử liên quan: W4-TV1-05.

### Nội dung thực hiện

- Phát kiểm tra topic `fooddelivery-order-events` và trạng thái đăng ký nhận thông báo qua email trên Amazon SNS.
- Đối chiếu output của `CommitAcceptedTransition` và `CommitCompletedTransition` trong execution E2E ở mục W4-TV1-03 để xác nhận kết quả publish SNS.
- Kiểm tra hộp thư để đối chiếu thông báo thực tế với kết quả publish SNS.

### Kết quả thực tế

- Topic `fooddelivery-order-events` có email subscription ở trạng thái `Confirmed`.
- Output của `CommitAcceptedTransition` ghi nhận `"sns": "PUBLISHED"`.
- Output của `CommitCompletedTransition` cũng ghi nhận `"sns": "PUBLISHED"`.
- Hộp thư email nhận được đủ 2 thông báo: một mail khi đơn chuyển sang `ACCEPTED v2` và một mail khi đơn chuyển sang `COMPLETED v4`.

### Minh chứng

| Nội dung | Minh chứng |
|---|---|
| Topic và Email Confirmed | [SnsSubscription](../../evidence/TanPhat/Week_04/W4-TV1-05_01_SnsSubscription.png) |
| Output CommitAccepted có PUBLISHED | [AcceptedPublish](../../evidence/TanPhat/Week_04/W4-TV1-05_02_AcceptedPublish.png) |
| Output CommitCompleted có PUBLISHED | [CompletedPublish](../../evidence/TanPhat/Week_04/W4-TV1-05_03_CompletedPublish.png) |
| Email thông báo nhận được trong hộp thư | [NotificationEmail](../../evidence/TanPhat/Week_04/W4-TV1-05_04_NotificationEmail.png) |

---

## W4-TV1-06 — Tổng hợp và bàn giao tài nguyên

- Toàn bộ script kiểm thử backend đã được lưu trong `tests/Week_04/`.
- File ASL workflow đang chạy thực tế trên Step Functions lưu tại `config/TanPhat/Week_04/w4-workflow-live.asl.json`.
- Nội dung bàn giao được ghi tại `design/Week_04/TV1_backend_handoff.md`, làm căn cứ để Huy đối chiếu và tổng hợp kết quả trong `tests/Week_04/results.md`.
- Các ảnh minh chứng đã được kiểm tra: không để lộ token bí mật hay access key AWS.
- Các ca kiểm thử của Phát được thực hiện trên tài khoản `053151184394` với role `LabRole`, trong phạm vi dịch vụ của đề tài trên AWS Academy Learner Lab.
