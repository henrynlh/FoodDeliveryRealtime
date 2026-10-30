# BÁO CÁO TIẾN BỘ TUẦN 3

## 1. Thông tin chung

- **Đề tài:** Ứng dụng giao đồ ăn – Theo dõi trạng thái đơn hàng theo thời gian thực.
- **Tên dự án:** FoodDeliveryRealtime.
- **Thời gian:** 19/10/2026 – 25/10/2026.
- **Nội dung trọng tâm:** Tích hợp hệ thống, hoàn thiện phân quyền, khôi phục kết nối và giám sát hoạt động.
- **Môi trường tích hợp:** AWS `us-east-1`.

## 2. Phân công nhiệm vụ và thời gian thực hiện

| STT | Họ và tên | MSSV | Nhiệm vụ đảm nhiệm | Giờ làm (h) |
| :---: | :--- | :---: | :--- | :---: |
| 1 | **Trương Tấn Phát** | 24110298 | Hoàn thiện Lambda Prepare/Submit/Commit, kiểm soát yêu cầu trùng và cạnh tranh, xử lý callback/timeout, kiểm thử backend và lập tài liệu giao tiếp. | Chưa tổng hợp |
| 2 | **Nguyễn Lê Huy** | 24110221 | Hoàn thiện giao diện và WebSocket dispatcher/broadcast, reconnect, phân quyền, logging; bổ sung lưu trạng thái timeout vào Orders và tổng hợp kiểm thử tích hợp. | Chưa tổng hợp |

**Thời gian thảo luận chung:** Chưa tổng hợp.

## 3. Chi tiết tiến độ thực hiện

### 3.1. Trương Tấn Phát

- Đồng bộ và rà soát mã nguồn ba Lambda nghiệp vụ cùng định nghĩa workflow Step Functions trên môi trường tích hợp.
- Hoàn thiện cơ chế xử lý bước chờ và cập nhật đơn hàng:
  - Prepare sử dụng điều kiện ghi để bảo vệ task đang CLAIMED hoặc DONE.
  - Submit claim bước chờ có điều kiện, nhận diện yêu cầu đã xử lý theo requestId và actorId.
  - Commit sử dụng DynamoDB TransactWriteItems để cập nhật Orders và WorkflowTasks đồng thời, kiểm soát version và tránh commit lặp.
- Kiểm tra yêu cầu dùng version cũ, chuyển sai thứ tự trạng thái, cập nhật đơn đã hoàn tất, callback không hợp lệ và hết thời hạn chờ.
- Theo kết quả kiểm thử TV1, gửi lại yêu cầu đã hoàn tất trả ALREADY_DONE, không tăng version hoặc phát thêm SNS trong trường hợp đã thử.
- Kiểm thử hai tài xế nhận cùng đơn bằng script gửi yêu cầu gần đồng thời: chỉ một tài xế nhận thành công, yêu cầu còn lại nhận CONFLICT; đối chiếu tài xế được giao trong Orders và WorkflowTasks.
- Bổ sung log JSON cho backend, đối chiếu dữ liệu theo mã đơn và yêu cầu xử lý.
- Bàn giao hợp đồng API, hướng dẫn triển khai, script kiểm thử, worklog và minh chứng các ca backend.

### 3.2. Nguyễn Lê Huy

- Hoàn thiện giao diện khách hàng và tài xế với trạng thái kết nối, snapshot đơn hàng và phản hồi thao tác. Các nút chuyển trạng thái chỉ được bật theo bước chờ và bị khóa khi đang gửi yêu cầu.
- Đồng bộ WebSocket dispatcher với backend TV1; bổ sung chuyển tiếp expectedVersion tới Lambda Submit và sử dụng danh tính do backend quản lý.
- Hoàn thiện khả năng khôi phục kết nối và dữ liệu:
  - Lưu mã đơn trong sessionStorage, không lưu token phiên.
  - Tự kết nối lại khi mạng được khôi phục, đăng ký theo dõi lại và đọc snapshot hiện tại.
  - Kiểm thử đơn thay đổi khi khách offline: sau reconnect, giao diện nhận ACCEPTED version 2 và tiếp tục nhận DELIVERING version 3.
  - Kiểm tra ngắt kết nối chủ động và khôi phục mã đơn sau tải lại trang.
- Kiểm thử dữ liệu có version cũ hoặc trùng bằng mô phỏng tại frontend; giao diện giữ trạng thái hiện tại. Khi gặp CONFLICT, giao diện khôi phục snapshot và nút thao tác; yêu cầu hợp lệ tiếp theo chuyển đơn sang DELIVERING version 3.
- Bổ sung kiểm thử phân quyền: C002/D002 bị từ chối đọc, theo dõi và cập nhật ngoài quyền; kết nối thiếu/sai token được ghi INVALID_SESSION. Kiểm thử D002 không nhận broadcast trái quyền sau khi D001 nhận đơn.
- Cấu hình và kiểm tra logging API Gateway stage dev: LoggingLevel INFO, DataTraceEnabled=false, Custom access logging tắt và sử dụng LabRole. Execution log ghi nhận route $default và integration status 200; log group API Gateway và năm Lambda tuần 3 có retention Never expire.
- Đối chiếu sai lệch execution FAILED nhưng Orders còn RUNNING, xác định nhánh Pass chỉ ghi dữ liệu execution. Bổ sung PersistWorkflowFailure để lưu workflowStatus và workflowEndedAt vào Orders, cùng Catch tại ba bước commit.
- Kiểm thử bản sửa timeout trên đơn mới ORD-381e33d0155909969f8f2d98: bước chờ nhận đơn hết hạn sau 300 giây; Orders giữ PLACED version 1, lưu TIMED_OUT và workflowEndedAt. Snapshot tài xế có readySteps rỗng, khóa các nút; execution FAILED theo state Fail được thiết kế.
- Tổng hợp kết quả TC01–TC13, cập nhật hướng dẫn triển khai, worklog, minh chứng và đưa các tệp bàn giao lên GitHub.

### 3.3. Kết quả tích hợp chung

- Lần hồi quy sau cập nhật dispatcher với đơn ORD-dcba07009952a36dee9e01f4 xác nhận C001/D001 thực hiện được luồng tạo → nhận → giao → hoàn tất. Đơn kết thúc COMPLETED version 4, driverId D001; workflowStatus và executionStatus đều SUCCEEDED.
- Các kết quả kiểm thử đã ghi nhận luồng nghiệp vụ, xử lý yêu cầu trùng/cạnh tranh theo hồ sơ TV1, realtime, reconnect và phân quyền trong phạm vi đã thực hiện.
- Sau bản sửa workflow, kiểm thử trên đơn mới xác nhận trạng thái timeout được lưu vào Orders trước khi execution kết thúc.
- Tài nguyên được giữ lại tại thời điểm kiểm thử. Ngày 25/10/2026, Learner Lab hiển thị Used $0 of $50 và thời gian tích lũy 18:35:00 (1115 phút). Đây là số liệu toàn lab, không phải chi phí hoặc giờ làm riêng tuần 3; chi phí tuần 3 chưa có số liệu tách riêng.

## 4. Công việc còn lại

- Chạy hồi quy luồng thành công đầy đủ sau bản sửa PersistWorkflowFailure; lần hồi quy thành công nêu trên diễn ra trước bản sửa này.
- Bổ sung kiểm thử riêng lỗi commit và timeout tại hai bước chờ còn lại. Kết quả timeout sau sửa hiện xác nhận bước PrepareAcceptedTask.
- Tách riêng kiểm thử khôi phục sau CONFLICT khi tắt polling; lần thử hiện tại vẫn bật đọc định kỳ.
- Tổng hợp thời gian làm việc thực tế và xác định SHA chính xác của phiên bản đã triển khai trên AWS. Các SHA bàn giao trong Git hiện ghi nhận phiên bản hồ sơ.

## 5. Hồ sơ và minh chứng

- [Worklog Trương Tấn Phát](TanPhat/Week_03.md).
- [Worklog Nguyễn Lê Huy](LeHuy/Week_03.md).
- [Kết quả kiểm thử TC01–TC13](../tests/Week_03/results.md).
- [Hợp đồng API](../design/Week_03/api_contract.md).
- [Hướng dẫn triển khai và vận hành](../design/Week_03/deployment.md).
- [Workflow tích hợp tuần 3](../config/LeHuy/Week_03/order_workflow_realtime.asl.json).
