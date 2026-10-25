# TÀI LIỆU TRIỂN KHAI VÀ VẬN HÀNH – TUẦN 3

- **Hệ thống:** FoodDeliveryRealtime.
- **Thời gian:** 19/10/2026 – 25/10/2026.
- **Vùng triển khai:** `us-east-1` (N. Virginia).
- **Tài khoản AWS tích hợp:** `165662523632`.
- **Execution Role:** `LabRole`.
- **TV1:** Trương Tấn Phát – 24110298. Phụ trách workflow và các Lambda prepare, submit, commit.
- **TV2:** Nguyễn Lê Huy – 24110221. Phụ trách WebSocket dispatcher, broadcast, giao diện và kiểm thử tích hợp phần TV2.
- **Vị trí tài liệu:** `design/Week_03/deployment.md`.

## 1. Cấu hình bảng DynamoDB

| Tên bảng | Partition Key | Sort Key | Biến môi trường tương ứng | Chức năng |
| --- | --- | --- | --- | --- |
| `fooddelivery-orders` | `orderId` (String) | Không có | `ORDERS_TABLE` | Lưu thông tin đơn hàng, trạng thái, version và tài xế phụ trách. |
| `fooddelivery-workflow-tasks` | `orderId` (String) | `step` (String) | `WORKFLOW_TASKS_TABLE` ở Lambda TV1; `TASKS_TABLE` ở Lambda TV2 | Lưu callback token và trạng thái bước chờ `READY`, `CLAIMED`, `DONE`. |
| `fooddelivery-connections` | `connectionId` (String) | Không có | `CONNECTIONS_TABLE` | Quản lý kết nối WebSocket, danh tính phiên và đơn đang theo dõi. |

Cấu hình bổ sung:

- Các bảng sử dụng chế độ dung lượng On-demand.
- Bảng Connections có GSI `ByOrderId`, partition key `orderId` (String), projection `ALL`.
- Bảng Connections sử dụng TTL với thuộc tính `expiresAt`.
- Code kiểm tra hạn sử dụng của kết nối trước khi xử lý yêu cầu và gửi broadcast.
- `WORKFLOW_TASKS_TABLE` và `TASKS_TABLE` cùng trỏ đến bảng `fooddelivery-workflow-tasks`. Hai tên biến khác nhau do mã nguồn TV1 và TV2 sử dụng tên cấu hình riêng.

## 2. Cấu hình Lambda Functions

### 2.1. Danh sách Lambda

| Tên Lambda | Handler theo mã nguồn | Execution Role | Thành viên phụ trách |
| --- | --- | --- | --- |
| `fooddelivery-prepare-task` | `lambda_function.lambda_handler` | `LabRole` | TV1 |
| `fooddelivery-submit-transition` | `lambda_function.lambda_handler` | `LabRole` | TV1 |
| `fooddelivery-commit-transition` | `lambda_function.lambda_handler` | `LabRole` | TV1 |
| `fooddelivery-ws-dispatcher` | `lambda_function.lambda_handler` | `LabRole` | TV2 |
| `fooddelivery-broadcast` | `lambda_function.lambda_handler` | `LabRole` | TV2 |

Runtime, memory và timeout cần được đối chiếu trên cấu hình thực tế của từng Lambda:

- **Code → Runtime settings:** kiểm tra runtime và handler.
- **Configuration → General configuration:** kiểm tra memory và timeout.
- **Configuration → Permissions:** kiểm tra execution role.

Không sử dụng thông số Python 3.12, 128 MB hoặc timeout trong bản tài liệu cũ làm cấu hình thực tế đã xác nhận nếu chưa đối chiếu trên Console.

### 2.2. Biến môi trường của Lambda TV1

| Lambda | Biến môi trường | Giá trị / mục đích |
| --- | --- | --- |
| `fooddelivery-prepare-task` | `WORKFLOW_TASKS_TABLE` | `fooddelivery-workflow-tasks` |
| `fooddelivery-submit-transition` | `WORKFLOW_TASKS_TABLE` | `fooddelivery-workflow-tasks` |
| `fooddelivery-commit-transition` | `ORDERS_TABLE` | `fooddelivery-orders` |
| `fooddelivery-commit-transition` | `WORKFLOW_TASKS_TABLE` | `fooddelivery-workflow-tasks` |
| `fooddelivery-commit-transition` | `SNS_TOPIC_ARN` | ARN thực tế của topic `fooddelivery-order-events`. |

Nếu phiên bản prepare hoặc submit đã tích hợp có đọc bảng Orders, bổ sung `ORDERS_TABLE=fooddelivery-orders` theo yêu cầu của mã nguồn đó.

### 2.3. Biến môi trường của fooddelivery-ws-dispatcher

| Biến môi trường | Giá trị / cách cấu hình |
| --- | --- |
| `ORDERS_TABLE` | `fooddelivery-orders` |
| `CONNECTIONS_TABLE` | `fooddelivery-connections` |
| `TASKS_TABLE` | `fooddelivery-workflow-tasks` |
| `STATE_MACHINE_ARN` | `arn:aws:states:us-east-1:165662523632:stateMachine:fooddelivery-order-workflow` |
| `SUBMIT_LAMBDA_ARN` | `arn:aws:lambda:us-east-1:165662523632:function:fooddelivery-submit-transition` |
| `SESSION_TOKENS_JSON` | JSON ánh xạ token phiên thử sang đối tượng có `id` và `role`. Cấu hình giá trị trực tiếp trên Lambda, không đưa token thật vào repository. |

Danh tính sử dụng trong kiểm thử:

- C001 và C002 có role `CUSTOMER`.
- D001 và D002 có role `DRIVER`.
- Dispatcher lấy danh tính từ bản ghi kết nối do backend tạo.
- Không sử dụng `actorId` hoặc role do trình duyệt tự cung cấp để xác định quyền.

### 2.4. Biến môi trường của fooddelivery-broadcast

| Biến môi trường | Giá trị |
| --- | --- |
| `ORDERS_TABLE` | `fooddelivery-orders` |
| `CONNECTIONS_TABLE` | `fooddelivery-connections` |
| `TASKS_TABLE` | `fooddelivery-workflow-tasks` |
| `WS_ENDPOINT_URL` | `https://lob1j5l21i.execute-api.us-east-1.amazonaws.com/dev` |

Tên biến endpoint đúng theo mã nguồn là `WS_ENDPOINT_URL`.

Broadcast vẫn cần `TASKS_TABLE` vì module `common.py` khởi tạo cả ba bảng khi được import.

## 3. Thứ tự triển khai trên AWS

### 3.1. Kiểm tra tài nguyên nền

1. Chọn đúng tài khoản tích hợp và region `us-east-1`.
2. Kiểm tra ba bảng DynamoDB đang Active.
3. Kiểm tra khóa chính, GSI `ByOrderId` và TTL của Connections.
4. Kiểm tra các Lambda, state machine và SNS topic.
5. Lưu bản code và định nghĩa workflow trước khi cập nhật.
6. Hoàn tất cập nhật các thành phần trước khi tạo đơn kiểm thử mới.

### 3.2. Triển khai ba Lambda backend của TV1

Cập nhật mã nguồn tương ứng:

1. [prepare-task/lambda_function.py](../../code/TanPhat/Week_03/prepare-task/lambda_function.py) lên `fooddelivery-prepare-task`.
2. [submit-transition/lambda_function.py](../../code/TanPhat/Week_03/submit-transition/lambda_function.py) lên `fooddelivery-submit-transition`.
3. [commit-transition/lambda_function.py](../../code/TanPhat/Week_03/commit-transition/lambda_function.py) lên `fooddelivery-commit-transition`.

Sau khi cập nhật:

- Kiểm tra biến môi trường của từng hàm.
- Kiểm tra handler.
- Nhấn **Deploy** nếu sửa code trực tiếp trên Lambda Console.
- Đối chiếu code triển khai với phiên bản lưu trong repository.

### 3.3. Triển khai WebSocket dispatcher của TV2

Lambda `fooddelivery-ws-dispatcher` cần có ba file:

- [lambda_function.py](../../code/LeHuy/Week_03/ws_dispatcher/lambda_function.py).
- [common.py](../../code/LeHuy/Week_03/ws_dispatcher/common.py).
- [orders_api.py](../../code/LeHuy/Week_03/ws_dispatcher/orders_api.py).

Thực hiện:

1. Đưa ba file vào cùng thư mục gốc của gói triển khai.
2. Kiểm tra đủ sáu biến môi trường tại mục 2.3.
3. Kiểm tra handler `lambda_function.lambda_handler`.
4. Nhấn **Deploy**.
5. Kiểm tra adapter trong `orders_api.py` chuyển tiếp đủ dữ liệu sang submit Lambda.

Payload gọi submit gồm:

```python
event = {
    "orderId": oid,
    "targetStatus": step,
    "actorId": actor["id"],
    "requestId": request,
    "expectedVersion": version
}
```

Adapter xử lý các trường trả về của submit:

- `ok`: kết quả xử lý yêu cầu.
- `status`: `QUEUED`, `PROCESSING` hoặc `ALREADY_DONE`.
- `errorCode`: mã lỗi nếu yêu cầu không thành công.

`QUEUED` chỉ xác nhận callback đã được gửi. Cần kiểm tra snapshot hoặc dữ liệu backend để xác nhận đơn đã commit.

### 3.4. Triển khai broadcast của TV2

Lambda `fooddelivery-broadcast` cần có:

- [lambda_function.py](../../code/LeHuy/Week_03/broadcast/lambda_function.py).
- [common.py](../../code/LeHuy/Week_03/ws_dispatcher/common.py) cùng phiên bản với module dùng chung của dispatcher.

Thực hiện:

1. Đặt hai file ở thư mục gốc của gói triển khai.
2. Kiểm tra đủ bốn biến môi trường tại mục 2.4.
3. Kiểm tra `WS_ENDPOINT_URL` dùng giao thức `https://`.
4. Nhấn **Deploy**.

Broadcast đọc lại bản ghi kết nối để kiểm tra:

- Kết nối vẫn tồn tại.
- Kết nối vẫn theo dõi đúng đơn.
- Phiên chưa hết hạn.
- Danh tính hiện tại còn quyền đọc đơn.

Nếu Management API trả `GoneException`, hàm gửi tin dọn bản ghi kết nối không còn tồn tại.

### 3.5. Cập nhật State Machine

Tài nguyên:

- State machine: `fooddelivery-order-workflow`.
- Loại workflow: Standard để sử dụng callback task token.

Các tệp cấu hình liên quan:

- [Workflow của TV1](../../config/TanPhat/Week_03/order_workflow.asl.json).
- [Workflow tích hợp realtime của TV2](../../config/LeHuy/Week_03/order_workflow_realtime.asl.json).

Thực hiện:

1. Mở **Step Functions → State machines → fooddelivery-order-workflow → Edit**.
2. Dùng bản [workflow TV2 tuần 3](../../config/LeHuy/Week_03/order_workflow_realtime.asl.json) đã đồng bộ từ CloudShell; đối chiếu với TV1 nhưng không ghi đè bằng bản thiếu PersistWorkflowFailure.
3. Kiểm tra ARN Lambda đúng tài khoản và region.
4. Kiểm tra workflow có đủ các bước prepare, commit và broadcast.
5. Validate và lưu định nghĩa.
6. Tạo đơn mới để kiểm thử định nghĩa vừa cập nhật.

Ba bước broadcast cần có:

- `BroadcastAccepted`.
- `BroadcastDelivering`.
- `BroadcastCompleted`.

Bản workflow tích hợp tuần 3 được đồng bộ từ `workflow-fixed-week3.json` tải từ CloudShell. Khi cập nhật, dùng bản TV2 đã có PersistWorkflowFailure; không lấy ASL cũ hoặc tự đổi workflow TV1 chỉ để làm hai tệp giống nhau. Các bước broadcast và luồng nghiệp vụ được giữ nguyên.

Execution đang chạy không tự chuyển sang định nghĩa workflow mới.

### 3.6. Kiểm tra SNS

1. Mở topic `fooddelivery-order-events`.
2. Kiểm tra email subscription đã được xác nhận.
3. Kiểm tra `SNS_TOPIC_ARN` trên Lambda `fooddelivery-commit-transition`.
4. Đối chiếu email thực nhận và log publish theo kịch bản kiểm thử của TV1.

Không kết luận SNS hoạt động chỉ dựa vào việc giao diện hiển thị đơn hoàn tất.

### 3.7. Kiểm tra API Gateway WebSocket

1. Kiểm tra route selection expression là `$request.body.action`.
2. Kiểm tra `$connect`, `$disconnect`, `$default` và các route action tạo riêng nếu có.
3. Kiểm tra integration trỏ đến dispatcher đang sử dụng.
4. Kiểm tra stage `dev` trỏ đến deployment hiện hành.
5. Nếu thay đổi route hoặc integration, triển khai lại API khi stage chưa bật auto-deploy.

Nếu chỉ cập nhật code Lambda và integration vẫn sử dụng đúng hàm hiện tại, không cần triển khai lại API Gateway.

### 3.8. Cập nhật giao diện và smoke test

Ba file frontend phải đặt cùng thư mục:

- [customer.html](../../code/LeHuy/Week_03/frontend/customer.html).
- [driver.html](../../code/LeHuy/Week_03/frontend/driver.html).
- [shared.js](../../code/LeHuy/Week_03/frontend/shared.js).

Thực hiện:

1. Mở hai giao diện và tải lại trang để nhận JavaScript mới.
2. Kết nối customer bằng phiên C001.
3. Kết nối driver bằng phiên D001.
4. Tạo đơn mới từ customer.
5. Cho driver theo dõi cùng mã đơn.
6. Thực hiện nhận đơn, bắt đầu giao và hoàn tất.
7. Kiểm tra hai giao diện nhận cập nhật.
8. Đọc lại đơn để xác nhận snapshot cuối và trạng thái execution.

Kết quả mong đợi:

| Mốc | Trạng thái đơn | Version |
| --- | --- | --- |
| Tạo đơn | `PLACED` | 1 |
| Nhận đơn | `ACCEPTED` | 2 |
| Bắt đầu giao | `DELIVERING` | 3 |
| Hoàn tất | `COMPLETED` | 4 |

Kết thúc luồng thành công:

- `driverId=D001`.
- `workflowStatus=SUCCEEDED`.
- `executionStatus=SUCCEEDED`.

## 4. Hướng dẫn vận hành và kiểm thử

### 4.1. Địa chỉ kết nối

Endpoint nhập trên giao diện:

```text
wss://lob1j5l21i.execute-api.us-east-1.amazonaws.com/dev/
```

Endpoint Management API dùng trong broadcast:

```text
https://lob1j5l21i.execute-api.us-east-1.amazonaws.com/dev
```

Token phiên thử được nhập vào giao diện. Không sử dụng AWS access key hoặc secret key làm token phiên.

### 4.2. Kiểm thử trên giao diện

Các nhóm kiểm thử của TV2 gồm:

- Tạo đơn và nhận cập nhật realtime.
- Gửi lại cùng yêu cầu tạo đơn.
- Trạng thái nút theo bước chờ.
- Gửi phiên bản cũ và xử lý `CONFLICT`.
- Đọc lại snapshot sau lỗi.
- Mất kết nối, kết nối lại và khôi phục đơn theo dõi.
- Nhận cập nhật mới sau khi kết nối lại.
- Khách hàng truy cập chéo đơn.
- Tài xế không được phân công cập nhật đơn.
- Kết nối thiếu token hoặc token sai.
- Broadcast sau khi tài xế mất quyền đọc đơn.

Kết quả thực tế được ghi tại [tests/Week_03/results.md](../../tests/Week_03/results.md).

Chỉ ghi Đạt khi đã có kết quả kiểm thử và minh chứng phù hợp.

### 4.3. Chạy script hỗ trợ kiểm thử

Chạy lệnh từ thư mục gốc repository.

Cài thư viện nếu máy chưa có:

```bash
py -m pip install websocket-client
```

Chuẩn bị `tests/Week_03/request.json` chứa payload và `requestId` của ca cần thử (tệp đầu vào này chưa được cung cấp sẵn), sau đó gửi yêu cầu:

```bash
py tests/Week_03/ws_request.py --request tests/Week_03/request.json --out evidence/TanPhat/Week_03/response.json
```

Script yêu cầu nhập endpoint và token phiên thử.

Để kiểm tra gửi lặp:

1. Giữ nguyên payload và `requestId`.
2. Gửi lại cùng yêu cầu.
3. Lưu kết quả hai lần chạy bằng hai tên output khác nhau.
4. Đối chiếu phản hồi, Orders và WorkflowTasks để xác nhận không commit hoặc tăng version thêm cho cùng yêu cầu chuyển trạng thái; kiểm tra tác động tới SNS và broadcast.

Kiểm thử hai tài xế cùng nhận đơn:

```bash
py tests/Week_03/race_accept.py
```

Điều kiện:

- Có một đơn mới `PLACED`, version 1.
- Bước ACCEPTED đang chờ callback.
- Có phiên thử D001 và D002.

Đối chiếu cả hai request/response với Orders và WorkflowTasks để xác định chỉ một tài xế nhận đơn thành công.

### 4.4. Tra cứu CloudWatch Logs

Vào **CloudWatch → Logs → Log groups**.

Các log group cần tra cứu:

- `/aws/lambda/fooddelivery-ws-dispatcher`.
- `/aws/lambda/fooddelivery-broadcast`.
- `/aws/lambda/fooddelivery-prepare-task`.
- `/aws/lambda/fooddelivery-submit-transition`.
- `/aws/lambda/fooddelivery-commit-transition`.

Cách đối chiếu:

1. Chọn khoảng thời gian tương ứng lần kiểm thử.
2. Tìm theo `orderId`, `requestId` hoặc mã lỗi được ghi trong log.
3. Đối chiếu với request và response trên giao diện.
4. Kiểm tra execution nếu có lỗi callback hoặc sai trạng thái.

Thời gian ISO kết thúc bằng `Z` là UTC. Khi đối chiếu giờ Việt Nam, cộng thêm 7 giờ.

### 4.5. Xử lý một số tình huống

| Hiện tượng | Cách kiểm tra |
| --- | --- |
| WebSocket không kết nối được | Kiểm tra endpoint, token và log `$connect` của dispatcher. |
| Nút chuyển trạng thái bị khóa | Đọc lại đơn, kiểm tra `readySteps`, trạng thái đơn và execution. |
| Submit trả `QUEUED` nhưng đơn chưa đổi | Chờ cập nhật hoặc đọc lại đơn, kiểm tra commit Lambda và execution. |
| Không nhận broadcast | Kiểm tra đơn đang theo dõi, quyền đọc, hạn phiên, endpoint và log broadcast. |
| Có lỗi `CONFLICT` | Đọc lại snapshot mới trước khi gửi thao tác tiếp theo. |
| Callback hết hạn | Kiểm tra timeout của bước chờ và trạng thái execution. |
| `workflowStatus` khác trạng thái execution | Kiểm tra nhánh lỗi và cập nhật Orders của TV1, ghi nhận sai lệch. |

Mã đóng WebSocket `1006` trên trình duyệt không đủ để khẳng định một HTTP status cụ thể.

Log broadcast tổng hợp `sent`, `skipped`, `gone` phải được kết hợp với ảnh giao diện và danh tính phiên. Bộ đếm tổng hợp không tự xác định kết nối nào bị bỏ qua.

### 4.6. Logging và quyền vận hành đã kiểm tra

Cấu hình ghi nhận ngày 25/10/2026:

| Thuộc tính | Giá trị đã xác nhận |
| --- | --- |
| API / stage | `fooddelivery-ws` / `dev` |
| LoggingLevel | `INFO` |
| DataTraceEnabled | `false` |
| Custom access logging | Tắt |
| CloudWatch Logs role ARN | `arn:aws:iam::165662523632:role/LabRole` |
| Log group API Gateway | `/aws/apigateway/lob1j5l21i/dev` |
| Retention | `Never expire` trên API Gateway và năm Lambda tuần 3 |

Năm Lambda gồm prepare-task, submit-transition, commit-transition, ws-dispatcher và broadcast. Execution log API Gateway ghi request route `$default`, gọi integration và phản hồi status `200`. Ảnh WebSocketLoggingConfigured thể hiện bước cấu hình trung gian Errors only; giá trị INFO cuối cùng được ghi theo lần kiểm tra/cập nhật CLI do TV2 báo cáo, không suy ra INFO từ ảnh trung gian đó.

Quyền thực tế đã dùng thành công: đọc/cập nhật cấu hình logging, xem log groups/events và cập nhật workflow. Kết quả này xác nhận phạm vi vận hành đã thực hiện, không phải kiểm toán mọi quyền IAM; chưa kiểm thử quyền sửa policy.

Minh chứng:

- [Retention năm Lambda](../../evidence/LeHuy/Week_03/W3-TV2-05_04_LambdaLogRetention.png).
- [Retention API Gateway](../../evidence/LeHuy/Week_03/W3-TV2-05_05_ApiGatewayLogRetention.png).
- [Execution log route $default, status 200](../../evidence/LeHuy/Week_03/W3-TV2-05_06_ApiGatewayExecutionLog.png).

### 4.7. Lưu trạng thái thất bại và kiểm thử timeout

Bản [workflow TV2](../../config/LeHuy/Week_03/order_workflow_realtime.asl.json) được đồng bộ nguyên nội dung từ `Downloads/workflow-fixed-week3.json`, bản tải từ CloudShell sau sửa và triển khai theo xác nhận của TV2.

- HandleTimeout ghi `workflowError.workflowStatus=TIMED_OUT`; HandleWorkflowError ghi `workflowError.workflowStatus=FAILED`.
- Cả hai chuyển sang PersistWorkflowFailure, gọi `arn:aws:states:::dynamodb:updateItem` trên `fooddelivery-orders` để lưu `workflowStatus` và `workflowEndedAt`.
- Điều kiện: đơn tồn tại, status chưa COMPLETED và executionArn chưa có hoặc trùng execution hiện tại. Không thay đổi status nghiệp vụ hay version.
- Sau khi lưu, chuyển WorkflowFailed (state Fail). Vì vậy executionStatus FAILED cùng workflowStatus TIMED_OUT là kết quả đúng của ca timeout này.
- Ba bước CommitAcceptedTransition, CommitDeliveringTransition và CommitCompletedTransition có Catch States.ALL chuyển HandleWorkflowError. Các bước broadcast và luồng nghiệp vụ được giữ nguyên.

Quy trình đã thực hiện trên đơn mới `ORD-381e33d0155909969f8f2d98`:

1. Tạo đơn PLACED version 1, không nhận đơn và chờ PrepareAcceptedTask timeout 300 giây.
2. Đối chiếu đường đi HandleTimeout → PersistWorkflowFailure → WorkflowFailed; PersistWorkflowFailure thành công.
3. Kiểm tra Orders giữ PLACED version 1, có workflowStatus TIMED_OUT và workflowEndedAt.
4. Đọc lại trên giao diện tài xế: snapshot TIMED_OUT, executionStatus FAILED, readySteps rỗng; các nút chuyển trạng thái bị khóa.

Minh chứng:

- [Workflow cũ kết thúc tại WorkflowFailed](../../evidence/LeHuy/Week_03/W3-TV2-06_06_WorkflowFailureCause.png).
- [Chi tiết callback timeout ở execution cũ](../../evidence/LeHuy/Week_03/W3-TV2-06_07_CallbackTimeoutDetails.png).
- [Snapshot tài xế sau sửa](../../evidence/LeHuy/Week_03/W3-TV2-06_08_TimeoutSnapshotAfterFix.png).
- [Workflow sau sửa](../../evidence/LeHuy/Week_03/W3-TV2-06_09_TimeoutWorkflowAfterFix.png).
- [Orders lưu TIMED_OUT và workflowEndedAt](../../evidence/LeHuy/Week_03/W3-TV2-06_10_TimeoutOrderPersisted.png).

Đạt lưu timeout ở bước chờ nhận đơn trên đơn mới. Chưa kiểm thử riêng lỗi commit, timeout ở hai bước chờ còn lại hoặc luồng thành công đầy đủ sau bản sửa workflow. Yêu cầu đến trễ chỉ được dẫn theo minh chứng TV1. Đơn cũ và execution cũ giữ nguyên lịch sử.

## 5. Minh chứng triển khai TV2

Thư mục lưu ảnh:

```text
evidence/LeHuy/Week_03/
```

| Tên ảnh | Nội dung minh chứng |
| --- | --- |
| `W3-TV2-01_01_DispatcherEnvironment.png` | Cấu hình biến môi trường dispatcher; đã che kín giá trị SESSION_TOKENS_JSON, giữ nguyên các pixel ngoài vùng che. |
| `W3-TV2-01_02_ExpectedVersionForwarded.png` | Mã nguồn adapter chuyển tiếp `expectedVersion`. |
| `W3-TV2-01_03_BroadcastEnvironment.png` | Bốn biến môi trường của broadcast. |
| `W3-TV2-01_04_CustomerAfterDeploy.png` | Khách hàng nhận cập nhật đến COMPLETED, version 4. |
| `W3-TV2-01_05_DriverAfterDeploy.png` | Tài xế đọc lại đơn và xác nhận workflow cùng execution SUCCEEDED. |

Ảnh code trong VS Code thể hiện nội dung mã nguồn trên máy cá nhân. Khi bàn giao, cần đối chiếu nội dung này với mã đã triển khai trên Lambda.

Kết quả hồi quy sau cập nhật dispatcher, trước bản sửa PersistWorkflowFailure:

| Nội dung | Kết quả |
| --- | --- |
| Order ID | `ORD-dcba07009952a36dee9e01f4` |
| Trạng thái cuối | `COMPLETED` |
| Version | 4 |
| Tài xế | `D001` |
| workflowStatus | `SUCCEEDED` |
| executionStatus sau khi đọc lại | `SUCCEEDED` |

Minh chứng trên xác nhận luồng thành công sau cập nhật dispatcher, trước khi sửa PersistWorkflowFailure. Không dùng lần thử này làm bằng chứng hồi quy toàn luồng sau bản sửa workflow. Kết quả timeout sau sửa được ghi riêng tại TC06.

## 6. Giới hạn môi trường và bảo vệ thông tin

- Sử dụng execution role `LabRole` do môi trường cung cấp.
- Chưa kiểm thử thao tác sửa IAM policy; không kết luận tài khoản bị cấm sửa IAM từ các thao tác logging đã thực hiện.
- Ngày 25/10/2026 đã đối chiếu retention Never expire trên log group API Gateway và năm Lambda tuần 3; đây là cấu hình tại thời điểm kiểm tra.
- Stage dev đã được xác nhận LoggingLevel INFO, DataTraceEnabled=false và Custom access logging tắt theo kết quả kiểm tra TV2.
- Không lưu token phiên thật, giá trị đầy đủ của `SESSION_TOKENS_JSON`, `taskToken` hoặc AWS credentials vào repository.
- Không đưa URL có token vào ảnh minh chứng công khai.
- Che kín giá trị token trong ảnh Environment variables trước khi commit.
- TTL của DynamoDB không thay thế timeout của Step Functions.
- Thời hạn `expiresAt` trong WorkflowTasks phải được đối chiếu với thời gian chờ callback của workflow.
- Trường hợp timeout từng để Orders ở RUNNING đã được sửa cho execution mới bằng PersistWorkflowFailure. Không sửa hồi tố execution hoặc bản ghi cũ.

Sai lệch timeout đã được xác định: các state Pass trước đây chỉ ghi kết quả vào dữ liệu execution, chưa cập nhật Orders. Bản sửa PersistWorkflowFailure đã được triển khai theo ghi nhận của TV2 và kiểm thử timeout trên đơn mới; lịch sử và bản ghi đơn cũ được giữ nguyên. Chi tiết tại mục 4.7.

## 7. Hồ sơ bàn giao

Các nội dung cần thống nhất trước khi nộp:

1. Code Lambda lưu trong repository khớp phiên bản đã triển khai.
2. Định nghĩa workflow lưu trong repository khớp bản tích hợp đang sử dụng.
3. [Kết quả kiểm thử tuần 3](../../tests/Week_03/results.md) ghi đúng trạng thái thực tế.
4. [Worklog TV1](../../worklog/TanPhat/Week_03.md) có kết quả, minh chứng và commit tương ứng.
5. [Worklog TV2](../../worklog/LeHuy/Week_03.md) có kết quả, minh chứng và commit tương ứng.
6. Thời gian làm việc được ghi theo thực tế.
7. Các liên kết ảnh và tệp mở được trên repository.
8. Các ảnh đã che thông tin phiên trước khi công khai.
9. Các mục chưa kiểm thử hoặc còn lỗi được ghi rõ, không đánh dấu Đạt.
