# Nhật kí làm việc tuần 2
Người thực hiện: Trương Tấn Phát - 24110298

Thời gian thực hiện:  tiếng

## Kiểm tra lại Invoke và Callback từ tuần 1

-   Ngày thực hiện: 14/10/2026.
-   Region: `us-east-1`.
-   State machine tuần 1 dùng để kiểm tra lại: `MyStateMachine`.
-   Lambda nền tảng tuần 1: `fooddelivery-foundation-test`.
-   Execution role: `LabRole` (xác nhận lại trong cấu hình thực tế).
-   Kiểm tra Invoke Lambda từ Step Functions: Thành công.
-   Kiểm tra callback `SendTaskSuccess`: Thành công.
-   Kết quả: Đạt.

### Minh chứng

-   [Execution Invoke Lambda thành công](../../evidence/TanPhat/Week_02/E-TV1-01_CheckInvoke.png)
-   [Execution callback thực tế](../../evidence/TanPhat/Week_02/E-TV1-02_CheckCallback.png)

## Thiết kế workflow nghiệp vụ

-   Ngày thực hiện: 14/10/2026.
-   Tệp định nghĩa: `config/Week_02/order_workflow.asl.json`
-   Loại workflow: Step Functions Standard.
-   Luồng nghiệp vụ mục tiêu:
    `PLACED → ACCEPTED → DELIVERING → COMPLETED`.
-   Cơ chế chờ: `waitForTaskToken` cho các bước chờ thao tác của nhân
    viên.
-   Kết quả deploy và chạy thử: Thành công.
-   Kết quả: Đạt.

### Minh chứng

-   [Workflow nghiệp vụ](../../evidence/TanPhat/Week_02/E-TV1-03_Workflow.png)
-   [Execution đang chờ ở trạng thái RUNNING.](../../evidence/TanPhat/Week_02/E-TV1-04_Waiting.png)

## Lambda `fooddelivery-workflow-tasks` -- đăng ký bước chờ callback

-   Ngày thực hiện: 14/10/2026.
-   Tệp mã nguồn: `code/TanPhat/fooddelivery-workflow-tasks/lambda_function.py`.
-   Function ARN: arn:aws:lambda:us-east-1:053151184394:function:fooddelivery-prepare-task.
-   Bảng lưu token: `fooddelivery-workflow-tasks`.
-   Khóa dữ liệu: `orderId` và `step`.
-   Task state ban đầu: READY.
-   Kết quả deploy và kiểm thử: Thành công.
-   Kết quả: Đạt.

### Minh chứng
-   [Tạo lambda phục vụ chờ callback.](../../evidence/TanPhat/Week_02/E-TV1-05_CreateLambda.png)
-   [Bản ghi WorkflowTasks có `orderId`, `step`, trạng thái READY; che`taskToken`.](../../evidence/TanPhat/Week_02/E-TV1-05_Orders.png)

## Lambda `submit_transition` -- tiếp nhận yêu cầu chuyển trạng thái

-   Ngày thực hiện: 14/10/2026.
-   Tệp mã nguồn: `code/TanPhat/fooddelivery-submit-transition/lambda_function.py`.
-   Function ARN: arn:aws:lambda:us-east-1:053151184394:function:fooddelivery-submit-transition.
-   Claim bước `READY → CLAIMED` có điều kiện: Thành công.
-   Callback `SendTaskSuccess`: Thành công.
-   Kết quả: Đạt.

### Minh chứng
-   [Tạo lambda phục vụ tiếp nhận yêu cầu chuyển trạng thái.](../../evidence/TanPhat/Week_02/E-TV1-07-CreateLambda.png)
-   [Execution sau khi callback được gửi.](../../evidence/TanPhat/Week_02/E-W2-TV1-02_Callback.png)
-   [Log hoặc kết quả request thể hiện `requestId`/xử lý xung đột; không
    chứa token.](%5BĐường%20dẫn%20ảnh%20minh%20chứng%20thực%20tế%5D)

## Lambda `commit_transition` -- cập nhật trạng thái đơn hàng

-   Ngày thực hiện: \[dd/mm/2026\].
-   Tệp mã nguồn: \[Đường dẫn thực tế\].
-   Function name/ARN: \[Ghi ARN thực tế\].
-   Bảng Orders: \[Tên bảng và khóa chính xác theo cấu hình thực tế\].
-   Quy tắc cập nhật: chỉ commit sau callback hợp lệ; kiểm tra trạng
    thái/version trước khi ghi.
-   Các trường cập nhật: `status`, `version`, `updatedAt`,
    `lastTransitionRequestId` \[điều chỉnh theo schema thực tế\].
-   `driverId` khi nhận đơn: \[Kết quả thực tế\].
-   Chống xử lý lặp/idempotence: \[Mô tả điều kiện hoặc transaction đã
    triển khai\].
-   Kết quả: \[Đạt / Chưa đạt / Bị chặn\].

### Minh chứng

-   [Orders sau khi chuyển sang ACCEPTED, gồm `driverId` và `version`
    đúng.](%60../../evidence/TanPhat/Week_02/E-W2-TV1-06_Accepted.png%60)
-   [Orders sau khi chuyển sang
    DELIVERING.](%60../../evidence/TanPhat/Week_02/E-W2-TV1-07_Delivering.png%60)
-   [Orders COMPLETED và execution
    Succeeded.](%60../../evidence/TanPhat/Week_02/E-W2-TV1-08_Completed.png%60)

## SNS -- thông báo sau khi commit

-   Ngày thực hiện: 14/10/2026.
-   Topic: `fooddelivery-order-events`.
-   Topic ARN: arn:aws:sns:us-east-1:053151184394:fooddelivery-order-events.
-   Sự kiện gửi thông báo: ACCEPTED.
-   Nội dung thông báo: có `orderId`, `status`, `actorId`, `timestamp`.
-   Thời điểm gửi: sau khi commit trạng thái thành công.
-   Email nhận được: Có.
-   Kết quả: Đạt.

### Minh chứng

-   [Email nhận được thông báo.](../../evidence/TanPhat/Week_02/sns.png)

## Kiểm thử workflow và xử lý lỗi

-   Ngày thực hiện: \[dd/mm/2026\].
-   Tệp kết quả: `tests/Week_02/results.md` \[điều chỉnh theo đường dẫn
    thực tế\].
-   Execution ARN: \[Ghi ARN thực tế\].
-   Order ID thử nghiệm: \[Ghi ID thực tế\].
-   Kết quả tổng quan: \[Số ca đạt / không đạt / bị chặn\].

  -----------------------------------------------------------------------------------
  Mã kiểm thử       Nội dung cần kiểm  Kết quả thực tế   Minh chứng
                    chứng                                
  ----------------- ------------------ ----------------- ----------------------------
  TC05              Chuyển trạng thái  \[Đạt/Không       \[Tên ảnh/link\]
                    hợp lệ và callback đạt/Bị chặn\]     
                    đúng bước                            

  TC06              Gửi lại cùng       \[Đạt/Không       \[Tên ảnh/link\]
                    `requestId`, không đạt/Bị chặn\]     
                    commit trùng                         

  TC07              Version hoặc trạng \[Đạt/Không       \[Tên ảnh/link\]
                    thái cũ bị từ chối đạt/Bị chặn\]     

  TC08              Hai nhân viên nhận \[Đạt/Không       `E-W2-TV1-09_Conflict.png`
                    cùng đơn: chỉ một  đạt/Bị chặn\]     
                    yêu cầu thắng                        

  TC09              Timeout/callback   \[Đạt/Không       `E-W2-TV1-10_Timeout.png`
                    lỗi không tự hoàn  đạt/Bị chặn\]     
                    tất đơn                              

  TC12              Kiểm thử thông báo \[Đạt/Không       `E-W2-TV1-11_SNS.png`
                    SNS sau commit     đạt/Bị chặn\]     
  -----------------------------------------------------------------------------------

### Minh chứng

-   [TC08: hai yêu cầu cạnh tranh, thể hiện yêu cầu thắng và yêu cầu
    xung
    đột.](%60../../evidence/TanPhat/Week_02/E-W2-TV1-09_Conflict.png%60)
-   [TC09: timeout và `workflowStatus` tương ứng; trạng thái nghiệp vụ
    không tự hoàn
    tất.](%60../../evidence/TanPhat/Week_02/E-W2-TV1-10_Timeout.png%60)
-   [Execution history, output và log của từng ca kiểm
    thử.](%5BĐường%20dẫn%20ảnh%20minh%20chứng%20thực%20tế%5D)

## Tích hợp với TV2

-   Ngày thực hiện: \[dd/mm/2026\].
-   Hợp đồng API/dữ liệu đã thống nhất: \[Đường dẫn `api_contract.md` và
    `data_dictionary.md` thực tế\].
-   Luồng đã thử: tạo đơn → Step Functions chờ → nhân viên thao tác →
    callback → commit Orders → WebSocket gửi `ORDER_UPDATED`.
-   Kết quả phía customer.html: \[Kết quả thực tế\].
-   Kết quả phía driver.html: \[Kết quả thực tế\].
-   Lỗi giao tiếp hoặc khác biệt schema: \[Ghi cụ thể\].
-   Người phối hợp và thời gian: \[Ghi thực tế\].
-   Kết quả: \[Đạt / Chưa đạt / Bị chặn\].

### Minh chứng

-   [Ảnh luồng thử từ giao diện hoặc API đến execution và trạng thái
    Orders.](%5BĐường%20dẫn%20ảnh%20minh%20chứng%20thực%20tế%5D)
-   [Ảnh giao diện nhận `ORDER_UPDATED` sau khi Orders đã được
    commit.](%5BĐường%20dẫn%20ảnh%20minh%20chứng%20thực%20tế%5D)

## Git, worklog và bàn giao

-   Ngày thực hiện: \[dd/mm/2026\].
-   Branch/commit: \[Ghi branch và commit thực tế\].
-   Link GitHub dạng `/blob/` đến ASL: \[Dán link\].
-   Link GitHub dạng `/blob/` đến ba Lambda: \[Dán link\].
-   Link GitHub dạng `/blob/` đến `tests/Week_02/results.md`: \[Dán
    link\].
-   Worklog: `worklog/TanPhat/Week_02.md` \[xác nhận đường dẫn thực
    tế\].
-   Thời gian thực tế: \[Ghi tổng giờ; yêu cầu môn học tối thiểu 8
    giờ/tuần, dự toán là 16 giờ\].
-   Công cụ AI đã sử dụng và phần việc được hỗ trợ: \[Khai báo trung
    thực\].
-   Trạng thái tài nguyên cuối phiên: \[Còn tồn tại / Đã xóa / Dùng
    chung với TV2\].
-   Chi phí: \[Ghi số liệu đã kiểm tra hoặc "Chưa xác nhận"; không suy
    đoán bằng 0\].
-   Kết quả bàn giao: \[Đạt / Chưa đạt / Bị chặn\].

## Tổng kết tuần 2

-   **Đã hoàn thành:** \[Chỉ liệt kê việc đã kiểm chứng\].
-   **Chưa hoàn thành:** \[Liệt kê việc còn thiếu\].
-   **Bị chặn và nguyên nhân:** \[Ghi nguyên văn lỗi, ảnh hưởng và người
    đã báo\].
-   **Việc chuyển sang tuần 3:** \[Danh sách công việc\].
-   **Tự đánh giá:** \[Đạt / Chưa đạt / Đạt một phần\].

### Checklist trước khi nộp

-   [ ] Đã thay toàn bộ nội dung trong dấu `[...]`.
-   [ ] Đường dẫn minh chứng đã được kiểm tra và ảnh thực sự tồn tại.
-   [ ] Không ghi "Đạt" nếu chưa có kết quả chạy thật.
-   [ ] Đã che `taskToken`, credentials và thông tin nhạy cảm.
-   [ ] Đã cập nhật kết quả kiểm thử, worklog và link GitHub `/blob/`.
-   [ ] Đã ghi rõ lỗi hoặc giới hạn Learner Lab.
-   [ ] Đã ghi trạng thái tài nguyên và chi phí theo dữ liệu thực tế.
