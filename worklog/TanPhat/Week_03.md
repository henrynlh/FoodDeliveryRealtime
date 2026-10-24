# Nhật ký làm việc tuần 3

- Người thực hiện: Trương Tấn Phát – 24110298.
- Vai trò: Thành viên 1 (TV1) — Phụ trách Backend, Workflow Step Functions, Lambda Prepare, Submit, Commit, DynamoDB Transactions và kiểm thử concurrency/idempotency.
- Người phối hợp: Nguyễn Lê Huy – 24110221 (Thành viên 2 — TV2).
- Môi trường: AWS `us-east-1` (tài khoản tích hợp của nhóm).
- Thời gian thực hiện: 21/10/2026 – 24/10/2026.
- Kết quả chung: Đạt 100% các tiêu chí kiểm thử backend độc lập và phối hợp tích hợp luồng thời gian thực.

---

## 1. Bảng tổng hợp công việc thực hiện (W3-TV1)

| Mã việc | Nội dung công việc | Sản phẩm bàn giao | Kết quả |
|---|---|---|---|
| **W3-TV1-01** | Đối chiếu backend đang chạy, cấu hình Runtime, Role và ASL nền tảng | Mã nguồn nền tảng trong repo và `design/Week_03/api_contract.md` | Đạt |
| **W3-TV1-02** | Rà soát & sửa backend: Chống ghi đè task, claim độc quyền và TransactWriteItems | Mã nguồn Lambda Prepare, Submit, Commit tuần 3 | Đạt |
| **W3-TV1-03** | Xử lý timeout 300s, cập nhật terminal status và bắt lỗi trong ASL | `config/TanPhat/Week_03/order_workflow.asl.json` | Đạt |
| **W3-TV1-04** | Chuẩn hóa Structured JSON Logging và kiểm tra quyền LabRole | Log group CloudWatch theo mã đơn, retention | Đạt |
| **W3-TV1-05** | Triển khai mã nguồn và ASL cập nhật lên môi trường AWS | Lambda & Step Functions deploy thành công | Đạt |
| **W3-TV1-06** | Thực hiện bộ kiểm thử toàn diện (TC01 – TC06, TC12, TC13) | Báo cáo kết quả và bộ minh chứng 53 tệp | Đạt |
| **W3-TV1-07** | Lập tài liệu triển khai, nhật ký tuần và commit Git | `worklog/TanPhat/Week_03.md`, `deployment.md` | Đạt |

---

## 2. Chi tiết các hạng mục triển khai

### W3-TV1-01: Đồng bộ mã nguồn và cấu hình nền tảng
- Đồng bộ mã nguồn từ AWS Lambda về repository local: `prepare-task`, `submit-transition`, `commit-transition`.
- Rà soát cấu hình: Runtime Python 3.12/3.13, Handler `lambda_function.lambda_handler`, Role `LabRole`, bộ nhớ 128 MB, timeout phù hợp.
- Lấy định nghĩa State Machine ASL hiện tại gồm các bước tích hợp WebSocket Broadcast của TV2.
- **Minh chứng:**
  - [Mã nguồn backend trong VS Code](../../evidence/TanPhat/Week_03/W3-TV1-01_01_BackendFiles.png)
  - [Cấu hình Lambda Prepare](../../evidence/TanPhat/Week_03/W3-TV1-01_02a_Prepare_Config.png)
  - [Role Lambda Prepare](../../evidence/TanPhat/Week_03/W3-TV1-01_02b_Prepare_Role.png)
  - [Cấu hình Lambda Submit](../../evidence/TanPhat/Week_03/W3-TV1-01_02c_Submit_Config.png)
  - [Role Lambda Submit](../../evidence/TanPhat/Week_03/W3-TV1-01_02d_Submit_Role.png)
  - [Cấu hình Lambda Commit](../../evidence/TanPhat/Week_03/W3-TV1-01_02e_Commit_Config.png)
  - [Role Lambda Commit](../../evidence/TanPhat/Week_03/W3-TV1-01_02f_Commit_Role.png)
  - [Sơ đồ Workflow nền tảng](../../evidence/TanPhat/Week_03/W3-TV1-01_03_WorkflowBaseline.png)

---

### W3-TV1-02: Rà soát & Cải tiến Logic Backend (Chống Race Condition & Idempotency)
- **Prepare Task:** Bổ sung conditional write ngăn chặn việc ghi đè vô điều kiện lên các task đang ở trạng thái `CLAIMED` hoặc `DONE` khi Step Functions thử lại (retry).
- **Submit Transition:**
  - Kiểm tra trạng thái task hiện tại; xử lý tính lũy thừa: nếu cùng `actorId` và `requestId` đã hoàn tất trả về `ALREADY_DONE`, nếu đang xử lý trả về `PROCESSING`.
  - Thực hiện nguyên tử bước Claim: chuyển trạng thái từ `READY` sang `CLAIMED` kèm điều kiện so sánh để tránh xung đột giữa nhiều tài xế.
- **Commit Transition:**
  - Sử dụng `TransactWriteItems` cập nhật đồng thời bảng `Orders` (tăng `version`, đổi `status`, gán `driverId`) và bảng `WorkflowTasks` (chuyển sang `DONE`, lưu `committedVersion`).
  - Kiểm tra điều kiện `attribute_exists` và `version` trước khi ghi để bảo vệ tính nhất quán dữ liệu.
  - Bỏ qua phát lặp SNS đối với các yêu cầu trùng lặp (`SKIPPED_DUPLICATE`).
- **Minh chứng:**
  - [Bảo vệ điều kiện ghi Prepare](../../evidence/TanPhat/Week_03/W3-TV1-02_01_PrepareGuard.png)
  - [Cơ chế Claim độc quyền tại Submit](../../evidence/TanPhat/Week_03/W3-TV1-02_02_SubmitClaim.png)
  - [Giao dịch TransactWriteItems tại Commit](../../evidence/TanPhat/Week_03/W3-TV1-02_03_CommitTransaction.png)

---

### W3-TV1-03 & W3-TV1-05: Cải tiến Workflow ASL và Triển khai
- Cập nhật ASL: Thêm nhánh bắt lỗi Catch và Task cập nhật trạng thái `workflowStatus = TIMED_OUT` vào bảng `Orders` khi xảy ra timeout 300 giây tại các bước chờ `waitForTaskToken`.
- Triển khai thành công mã nguồn lên các hàm Lambda và lưu định nghĩa workflow mới vào Step Functions.
- **Minh chứng:**
  - [Cấu hình xử lý Timeout trong ASL](../../evidence/TanPhat/Week_03/W3-TV1-03_01_TimeoutHandler.png)
  - [Triển khai mã Lambda thành công](../../evidence/TanPhat/Week_03/W3-TV1-05_01_DeploySuccess.png)
  - [Sơ đồ Workflow sau khi cập nhật](../../evidence/TanPhat/Week_03/W3-TV1-05_02_WorkflowFinal.png)

---

### W3-TV1-04: Chuẩn hóa Logs và Kiểm tra Quyền
- Cấu hình Structured JSON Logging trên toàn bộ các hàm backend (log đầy đủ `operation`, `orderId`, `step`, `actorId`, `requestId`, `version`), tuyệt đối không in lộ `taskToken` hay thông tin nhạy cảm.
- Kiểm tra cấu hình log retention của CloudWatch Log Groups.
- **Minh chứng:**
  - [Structured Log của Lambda Prepare](../../evidence/TanPhat/Week_03/W3-TV1-04_02_PrepareLog.png)
  - [Structured Log của Lambda Submit](../../evidence/TanPhat/Week_03/W3-TV1-04_03_SubmitLog.png)
  - [Structured Log của Lambda Commit](../../evidence/TanPhat/Week_03/W3-TV1-04_04_CommitLog.png)
  - [Cấu hình Log Retention trên CloudWatch](../../evidence/TanPhat/Week_03/W3-TV1-04_05_Retention.png)

---

## 3. Kết quả Kiểm thử chi tiết (Test Cases)

### Bảng tổng hợp kết quả kiểm thử

| Mã ca test | Tên ca kiểm thử | Kết quả | Minh chứng chính |
|---|---|---|---|
| **W3-TC01** | Hồi quy luồng E2E hoàn chỉnh (`PLACED → COMPLETED`) | **ĐẠT** | 9 ảnh minh chứng luồng đơn, bảng Orders v4, 3 task DONE và SNS |
| **W3-TC02** | Gửi lặp lại cùng yêu cầu chuyển trạng thái (Idempotency) | **ĐẠT** | Báo ALREADY_DONE, version giữ nguyên v2, không bắn trùng SNS |
| **W3-TC03** | Gửi yêu cầu với expectedVersion cũ (Stale Version) | **ĐẠT** | Từ chối CONFLICT, dữ liệu đơn không bị ghi đè |
| **W3-TC04** | Kiểm tra sai bước nghiệp vụ và cập nhật sau khi hoàn tất | **ĐẠT** | Chặn nhảy cóc bước và chặn sửa đơn đã COMPLETED |
| **W3-TC05** | Callback token giả mạo và gọi lại Submit/Commit | **ĐẠT** | Step Functions báo InvalidToken, Lambda xử lý an toàn |
| **W3-TC06** | Hết thời gian chờ (Timeout 300 giây) | **ĐẠT** | Workflow chuyển TIMED_OUT, từ chối nhận đơn trễ |
| **W3-TC12** | Hai tài xế tranh nhận một đơn đồng thời (Race Condition) | **ĐẠT** | Duy nhất 1 tài xế nhận đơn, tài xế còn lại nhận CONFLICT |

---

### Chi tiết và Minh chứng từng Ca kiểm thử

#### 1. W3-TC01 — Hồi quy luồng hoàn chỉnh sau cập nhật backend
- Kiểm tra luồng trạng thái từ khi tạo đơn đến khi hoàn tất: `PLACED (v1) → ACCEPTED (v2) → DELIVERING (v3) → COMPLETED (v4)`.
- Dữ liệu cuối cùng: Bảng `Orders` ghi nhận trạng thái `COMPLETED`, `version: 4`, `driverId: D001`. Bảng `WorkflowTasks` ghi nhận cả 3 bước đều `DONE`.
- Minh chứng:
  - [Đơn hàng mới tạo PLACED v1](../../evidence/TanPhat/Week_03/W3-TV1-TC01_01_Placed.png)
  - [Chuyển trạng thái ACCEPTED v2](../../evidence/TanPhat/Week_03/W3-TV1-TC01_02_Accepted.png)
  - [Chuyển trạng thái DELIVERING v3](../../evidence/TanPhat/Week_03/W3-TV1-TC01_03_Delivering.png)
  - [Hoàn tất đơn hàng COMPLETED v4](../../evidence/TanPhat/Week_03/W3-TV1-TC01_04_Completed.png)
  - [Dữ liệu cuối cùng trên bảng Orders](../../evidence/TanPhat/Week_03/W3-TV1-TC01_05_Orders.png)
  - [Cả 3 bước chờ đều DONE trong Tasks](../../evidence/TanPhat/Week_03/W3-TV1-TC01_06_TasksDone.png)
  - [Execution Step Functions Succeeded](../../evidence/TanPhat/Week_03/W3-TV1-TC01_07_Execution.png)
  - [Thông báo SNS ACCEPTED](../../evidence/TanPhat/Week_03/W3-TV1-TC01_08_SNSAccepted.png)
  - [Thông báo SNS COMPLETED](../../evidence/TanPhat/Week_03/W3-TV1-TC01_09_SNSCompleted.png)

#### 2. W3-TC02 — Gửi lại cùng yêu cầu (Idempotency)
- Gửi yêu cầu nhận đơn lần 1: Đơn được ghi nhận `ACCEPTED v2`.
- Gửi lại chính xác payload với cùng `requestId` và `actorId`: Hệ thống nhận diện yêu cầu cũ, trả về phản hồi an toàn (`ALREADY_DONE`), không tăng version, không sinh thông báo SNS thứ hai.
- Minh chứng:
  - [Phản hồi yêu cầu lần đầu](../../evidence/TanPhat/Week_03/W3-TV1-TC02_01_FirstResponse.png)
  - [Trạng thái Orders trước khi replay](../../evidence/TanPhat/Week_03/W3-TV1-TC02_02_BeforeReplay.png)
  - [Phản hồi khi replay cùng yêu cầu](../../evidence/TanPhat/Week_03/W3-TV1-TC02_03_ReplayResponse.png)
  - [Dữ liệu Orders giữ nguyên sau replay](../../evidence/TanPhat/Week_03/W3-TV1-TC02_04_AfterReplay.png)
  - [Bản ghi Task DONE với requestId cũ](../../evidence/TanPhat/Week_03/W3-TV1-TC02_05_TaskDone.png)
  - [Kiểm tra không phát lặp thông báo SNS](../../evidence/TanPhat/Week_03/W3-TV1-TC02_06_NotificationCheck.png)

#### 3. W3-TC03 — Phiên bản cũ (Stale Expected Version)
- Đơn đang ở trạng thái `ACCEPTED v2`, gửi yêu cầu chuyển sang `DELIVERING` nhưng truyền `expectedVersion: 1`.
- Backend kiểm tra điều kiện lạc quan, phát hiện version không khớp và từ chối với lỗi `CONFLICT`. Dữ liệu đơn không bị thay đổi.
- Minh chứng:
  - [Trạng thái đơn trước khi gửi stale request](../../evidence/TanPhat/Week_03/W3-TV1-TC03_01_Before.png)
  - [Phản hồi lỗi CONFLICT từ backend](../../evidence/TanPhat/Week_03/W3-TV1-TC03_02_StaleResponse.png)
  - [Dữ liệu bảng Orders không bị biến đổi](../../evidence/TanPhat/Week_03/TV1-TC03_03_AfterUnchanged.png)

#### 4. W3-TC04 — Sai bước và Sau hoàn tất
- **Nhảy cóc bước:** Đơn đang ở `PLACED v1`, cố tình gửi yêu cầu chuyển thẳng sang `DELIVERING` -> Backend từ chối hợp lệ.
- **Cập nhật sau hoàn tất:** Đơn đã ở `COMPLETED v4`, gửi yêu cầu thay đổi trạng thái -> Backend bảo vệ không cho phép ghi đè.
- Minh chứng:
  - [Phản hồi từ chối khi nhảy cóc bước](../../evidence/TanPhat/Week_03/W3-TV1-TC04_01_WrongStepResponse.png)
  - [Đơn vẫn giữ nguyên PLACED v1](../../evidence/TanPhat/Week_03/W3-TV1-TC04_02_PlacedUnchanged.png)
  - [Phản hồi từ chối cập nhật đơn đã hoàn tất](../../evidence/TanPhat/Week_03/W3-TV1-TC04_03_AfterCompletedResponse.png)

#### 5. W3-TC05 — Callback sai và Gọi lại Commit
- Gửi callback bằng token không hợp lệ (`W3-INVALID-TOKEN`) qua Step Functions API -> Step Functions từ chối với `InvalidToken`, execution tiếp tục chờ và không bị đổ vỡ.
- Test lặp trực tiếp trên Lambda Submit và Commit -> Lambda nhận diện duplicate và trả về kết quả an toàn.
- Minh chứng:
  - [CloudShell báo lỗi InvalidToken khi gửi token giả](../../evidence/TanPhat/Week_03/W3-TV1-TC05_01_InvalidToken.png)
  - [Dữ liệu đơn không bị ảnh hưởng](../../evidence/TanPhat/Week_03/W3-TV1-TC05_02_OrderUnchanged.png)
  - [Execution vẫn Running chờ callback hợp lệ](../../evidence/TanPhat/Week_03/W3-TV1-TC05_03_ExecutionWaiting.png)
  - [Lambda Submit xử lý an toàn khi gọi lại](../../evidence/TanPhat/Week_03/W3-TV1-TC05_04_SubmitReplay.png)
  - [Lambda Commit báo duplicate và không tăng version](../../evidence/TanPhat/Week_03/W3-TV1-TC05_05_CommitReplay.png)
  - [Dữ liệu cuối cùng được bảo toàn](../../evidence/TanPhat/Week_03/W3-TV1-TC05_06_FinalData.png)

#### 6. W3-TC06 — Hết thời gian chờ (Timeout)
- Khởi tạo đơn mới và giữ nguyên không nhận đơn trong 300 giây (5 phút).
- Step Functions tự động kích hoạt nhánh timeout, kết thúc execution và cập nhật `workflowStatus = TIMED_OUT` trên DynamoDB. Yêu cầu nhận đơn gửi muộn sau đó đều bị từ chối.
- Minh chứng:
  - [Đồ thị Step Functions đang chờ ở PrepareAcceptedTask](../../evidence/TanPhat/Week_03/W3-TV1-TC06_01_Waiting.png)
  - [Đồ thị rẽ sang nhánh xử lý Timeout sau 300s](../../evidence/TanPhat/Week_03/W3-TV1-TC06_02_TimeoutGraph.png)
  - [Bảng Orders ghi nhận workflowStatus TIMED_OUT](../../evidence/TanPhat/Week_03/W3-TV1-TC06_03_OrdersAfterTimeout.png)
  - [Yêu cầu nhận đơn trễ bị backend từ chối](../../evidence/TanPhat/Week_03/W3-TV1-TC06_04_LateRequestRejected.png)

#### 7. W3-TC12 — Hai tài xế tranh nhận một đơn (Race Condition)
- Chạy kịch bản 2 luồng đồng thời từ AWS CloudShell bằng `threading.Barrier`: Tài xế `D001` và `D002` gửi yêu cầu nhận cùng đơn `ORD-TC12-RACE-01` tại cùng một thời điểm.
- Kết quả: Cơ chế khóa có điều kiện hoạt động chuẩn xác: 1 tài xế claim thành công, tài xế còn lại bị từ chối ngay lập tức với `CONFLICT` ("This step is already claimed by another request.").
- Bảng `Orders` và `WorkflowTasks` chỉ gán đơn duy nhất cho người thắng cuộc.
- Minh chứng:
  - [Trạng thái đơn và task READY trước tranh chấp](../../evidence/TanPhat/Week_03/W3-TV1-TC12_01_BeforeRace.png)
  - [Kết quả đối lập của 2 tài xế trên CloudShell](../../evidence/TanPhat/Week_03/W3-TV1-TC12_02_TwoResponses.png)
  - [Bảng Orders chỉ ghi nhận duy nhất 1 tài xế](../../evidence/TanPhat/Week_03/W3-TV1-TC12_03_OrdersWinner.png)
  - [Bảng WorkflowTasks gán quyền cho người thắng](../../evidence/TanPhat/Week_03/W3-TV1-TC12_04_TaskWinner.png)

---

## 4. Phối hợp với Thành viên 2 (TV2 — Nguyễn Lê Huy)

- Phối hợp chốt chuẩn hợp đồng giao tiếp `api_contract.md`: Dispatcher trích xuất danh tính `actorId` từ WebSocket connection và chuyển tiếp an toàn xuống Lambda Submit.
- Đồng bộ trường `expectedVersion` và cấu trúc thông báo cập nhật `ORDER_UPDATED` theo thời gian thực tới `customer.html` và `driver.html`.
- Đồng bộ kịch bản xử lý timeout và khôi phục snapshot khi client reconnect.
- Chia sẻ dữ liệu kiểm thử backend để TV2 tổng hợp báo cáo kết quả chung tại `tests/Week_03/results.md`.

---

## 5. Hỗ trợ từ Công cụ AI

- Sử dụng AI hỗ trợ:
  - Xây dựng tài liệu hướng dẫn kỹ thuật chi tiết theo chuẩn mực của đồ án.
  - Rà soát các trường hợp biên của giao dịch DynamoDB (`TransactWriteItems`), cơ chế khóa lạc quan và chiến lược idempotent.
  - Soạn thảo script kiểm thử đồng thời (concurrency testing) trên AWS CloudShell.
- Toàn bộ các ca kiểm thử, thao tác console, triển khai mã nguồn và thu thập bằng chứng 53 tệp ảnh đều được sinh viên thực hiện và kiểm chứng trực tiếp trên môi trường AWS.
