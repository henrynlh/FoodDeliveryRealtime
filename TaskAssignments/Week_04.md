# KẾ HOẠCH THỰC HIỆN TUẦN 4 – FOODDELIVERYREALTIME

- **Thời gian:** 26/10/2026 – 01/11/2026.
- **TV1:** Trương Tấn Phát – MSSV 24110298.
- **TV2:** Nguyễn Lê Huy – MSSV 24110221.
- **Môi trường triển khai:** AWS us-east-1.
- **Execution Role:** `LabRole`.
- **Trạng thái:** Kế hoạch dự kiến; kết quả và thời gian thực tế được cập nhật sau khi thực hiện.

## 1. Mục tiêu

Hoàn thiện hệ thống sau đợt tích hợp tuần 3, kiểm thử hồi quy trên phiên bản thống nhất và chuẩn bị bộ hồ sơ trình diễn, bàn giao.

Các mục tiêu cụ thể:

- Xác nhận luồng tạo, nhận, giao và hoàn tất đơn hoạt động sau cập nhật workflow.
- Kiểm tra tính nhất quán giữa Orders, WorkflowTasks, execution và giao diện.
- Kiểm thử nhánh lỗi commit đã bổ sung nhưng chưa được kiểm thử riêng trong tuần 3.
- Hoàn thiện cách hiển thị trạng thái kết thúc trên giao diện.
- Đối chiếu log ứng dụng với log API Gateway.
- Chuẩn hóa mã nguồn, cấu hình, minh chứng và tài liệu triển khai.
- Hoàn thiện báo cáo đồ án, chuẩn bị video demo không quá 10 phút và ghi nhận chi phí thực tế.
- Lập danh sách tài nguyên cần giữ hoặc dọn dẹp sau bàn giao; chỉ dọn dẹp theo yêu cầu học phần.

## 2. Căn cứ và đầu vào

- [Kế hoạch tuần 3](Week_03.md).
- [Kết quả kiểm thử tuần 3](../tests/Week_03/results.md).
- [Tài liệu triển khai tuần 3](../design/Week_03/deployment.md).
- [Worklog TV1 tuần 3](../worklog/TanPhat/Week_03.md).
- [Worklog TV2 tuần 3](../worklog/LeHuy/Week_03.md).

Các kết quả kế thừa:

- Luồng nghiệp vụ chính đã hoàn tất với đơn COMPLETED, version 4.
- Dispatcher chuyển tiếp expectedVersion sang submit Lambda.
- Đã kiểm thử reconnect khi đơn thay đổi trong thời gian offline.
- Đã kiểm thử truy cập trái quyền và lọc broadcast.
- API Gateway đã ghi execution log, Data tracing tắt.
- Nhánh timeout đã cập nhật Orders qua PersistWorkflowFailure.

Các nội dung cần tiếp tục:

- Kiểm thử hồi quy toàn luồng sau bản sửa PersistWorkflowFailure.
- Kiểm thử riêng nhánh lỗi commit.
- Rà soát trạng thái WorkflowTasks sau khi workflow kết thúc.
- Hoàn thiện thông báo timeout và lỗi trên giao diện.
- Chốt phiên bản mã nguồn, tài liệu và minh chứng bàn giao.

## 3. Phạm vi thực hiện

### 3.1. Trong phạm vi

- Hoàn thiện và kiểm thử các chức năng hiện có.
- Sửa lỗi phát hiện trong quá trình kiểm thử.
- Cải thiện giao diện phục vụ trình diễn.
- Hoàn thiện logging và tài liệu vận hành.
- Ghi nhận cấu hình, phiên bản mã và chi phí.

### 3.2. Ngoài phạm vi

- Thanh toán trực tuyến.
- Bản đồ và định vị tài xế.
- Xác thực người dùng production.
- Bổ sung dịch vụ AWS ngoài nhu cầu của đề tài.
- Kiểm thử tải lớn hoặc thay đổi kiến trúc khi chưa có yêu cầu.

## 4. Phân công TV1 – Trương Tấn Phát

| Mã | Công việc | Cách thực hiện | Sản phẩm và tiêu chí hoàn thành |
| --- | --- | --- | --- |
| W4-TV1-01 | Đối chiếu workflow tích hợp | So sánh định nghĩa trên AWS với bản được nhóm chọn trong repository. Kiểm tra prepare, commit, broadcast, Catch và PersistWorkflowFailure. | Có bản workflow thống nhất và ghi rõ phiên bản triển khai. |
| W4-TV1-02 | Kiểm thử lỗi commit | Chuẩn bị dữ liệu thử riêng để tạo xung đột có kiểm soát trước bước commit. Không sửa hoặc phá dữ liệu đang dùng trình diễn. | Execution đi vào nhánh lỗi; Orders phản ánh trạng thái kết thúc phù hợp, không chuyển sai nghiệp vụ. |
| W4-TV1-03 | Kiểm tra WorkflowTasks sau kết thúc | Đối chiếu task DONE của đơn thành công và task còn lại của đơn timeout/lỗi. Kiểm tra callback đến trễ; phối hợp TV2 kiểm thử timeout tại hai bước chờ còn lại, giữ nguyên status nghiệp vụ và version khi ghi trạng thái kết thúc. | Ghi rõ trạng thái task, hiệu lực callback và kết quả yêu cầu đến trễ. |
| W4-TV1-04 | Hồi quy gửi lặp và tranh chấp | Chạy lại các ca có khả năng bị ảnh hưởng bởi thay đổi workflow. Đối chiếu request/response và dữ liệu cuối. | Không có chuyển trạng thái trùng; chỉ một tài xế nhận đơn trong ca tranh chấp. |
| W4-TV1-05 | Đối chiếu SNS | Kiểm tra thông báo ở các mốc được thiết kế và ghi nhận trường hợp publish lỗi nếu có. | Có log hoặc email minh chứng; mô tả đúng giới hạn giao thông báo. |
| W4-TV1-06 | Hoàn thiện tài liệu backend | Cập nhật cấu hình, quyền cần dùng, cách xử lý lỗi và kết quả kiểm thử. | Worklog, mã nguồn và minh chứng khớp phiên bản bàn giao. |

## 5. Phân công TV2 – Nguyễn Lê Huy

| Mã | Công việc | Cách thực hiện | Sản phẩm và tiêu chí hoàn thành |
| --- | --- | --- | --- |
| W4-TV2-01 | Kiểm thử hồi quy toàn luồng | Tạo đơn mới trên phiên bản workflow đã sửa. Thực hiện nhận, giao, hoàn tất và đối chiếu hai giao diện. | COMPLETED version 4, cùng driverId, execution SUCCEEDED. |
| W4-TV2-02 | Hoàn thiện trạng thái kết thúc trên giao diện | Hiển thị rõ đơn hết thời gian chờ hoặc workflow thất bại. Phân biệt trạng thái nghiệp vụ với trạng thái workflow. | Đơn PLACED nhưng workflow TIMED_OUT không chỉ hiển thị “Chờ tài xế nhận”; các nút không hợp lệ bị khóa. |
| W4-TV2-03 | Rà soát polling và reconnect | Kiểm tra ngắt kết nối chủ động, reconnect, đọc lại snapshot và dừng polling khi workflow đã kết thúc. | Không tự reconnect sau thao tác ngắt chủ động; không tiếp tục polling định kỳ khi không còn cần thiết. |
| W4-TV2-04 | Kiểm thử phục hồi sau CONFLICT | Tắt polling trong lần thử riêng. Gửi version cũ, quan sát lỗi và snapshot được đọc lại bởi cơ chế xử lý lỗi. | Xác nhận độc lập khả năng phục hồi sau CONFLICT, không dựa vào polling. |
| W4-TV2-05 | Đối chiếu logging | Ghép request thử với log dispatcher và API Gateway theo thời gian, request ID khi có. | Có minh chứng truy vết một yêu cầu thực tế, không ghi token hoặc dữ liệu nhạy cảm. |
| W4-TV2-06 | Chuẩn hóa giao diện trình diễn | Rà soát nhãn, thông báo, bố cục và khả năng sử dụng trên hai cửa sổ trình duyệt. | Hai giao diện dễ thao tác, hiển thị lỗi rõ ràng và không làm mất chức năng hiện có. |
| W4-TV2-07 | Tổng hợp hồ sơ bàn giao | Cùng TV1 hoàn thiện báo cáo đồ án và video demo không quá 10 phút; tổng hợp kết quả kiểm thử, hướng dẫn sử dụng, tài nguyên và chi phí. | Có báo cáo, video demo, tài liệu và minh chứng thống nhất, liên kết hợp lệ và commit tương ứng. |

## 6. Công việc phối hợp

| Mã | Nội dung | Phối hợp | Tiêu chí |
| --- | --- | --- | --- |
| W4-INT-01 | Chốt phiên bản triển khai | TV1 chốt backend và workflow; TV2 chốt dispatcher, broadcast, frontend. | Ghi nhận commit và cấu hình của phiên bản đưa vào kiểm thử. |
| W4-INT-02 | Kiểm thử tích hợp sau sửa | TV2 thao tác giao diện, TV1 đối chiếu dữ liệu và execution. | Kết quả frontend và backend thống nhất trên cùng mã đơn. |
| W4-INT-03 | Xử lý lỗi phát hiện | Thành viên phụ trách sửa đúng thành phần, người còn lại kiểm tra phần tích hợp liên quan. | Có nguyên nhân, thay đổi và kết quả kiểm thử lại. |
| W4-INT-04 | Chạy thử kịch bản trình diễn | Hai thành viên thực hiện vai khách hàng và tài xế. | Hoàn thành các bước demo trong thời gian chờ workflow. |
| W4-INT-05 | Kiểm tra hồ sơ nộp | Đối chiếu tài liệu, minh chứng, mã nguồn và lịch sử commit. | Không có liên kết hỏng, token thật hoặc kết quả chưa thử được ghi Đạt. |

## 7. Kế hoạch kiểm thử tuần 4

| Mã | Nội dung | Phụ trách chính | Kết quả mong đợi |
| --- | --- | --- | --- |
| W4-TC01 | Toàn luồng sau cập nhật workflow | TV2, phối hợp TV1 | COMPLETED version 4, execution SUCCEEDED, dữ liệu hai phía thống nhất. |
| W4-TC02 | Timeout tại các bước chờ và thông báo giao diện | TV2, phối hợp TV1 | Thử trên các đơn riêng tại bước chờ nhận, giao và hoàn tất. Orders lưu TIMED_OUT và workflowEndedAt, giữ status nghiệp vụ/version trước timeout; execution FAILED theo state Fail. Giao diện hiển thị rõ timeout, khóa nút và dừng polling theo thiết kế. |
| W4-TC03 | Lỗi commit có kiểm soát | TV1 | Không chuyển sai nghiệp vụ; nhánh lỗi lưu trạng thái kết thúc vào Orders. |
| W4-TC04 | Callback đến sau timeout | TV1 | Yêu cầu bị từ chối, status và version không đổi. |
| W4-TC05 | CONFLICT khi tắt polling | TV2 | Giao diện tự đọc lại snapshot qua cơ chế xử lý lỗi và phục hồi thao tác phù hợp. |
| W4-TC06 | Reconnect và ngắt chủ động | TV2 | Khôi phục snapshot khi reconnect; ngắt chủ động không tự kết nối lại. |
| W4-TC07 | Hồi quy gửi lặp và tranh nhận đơn | TV1 | Không có chuyển trạng thái trùng; dữ liệu cuối chỉ có một tài xế nhận đơn. |
| W4-TC08 | Truy vết request qua log | TV2 | Đối chiếu được yêu cầu thử với log API Gateway và dispatcher. |
| W4-TC09 | Kịch bản trình diễn tổng hợp | Cả hai | Luồng demo hoàn tất, minh chứng và dữ liệu cuối phù hợp. |

Thực hiện đầy đủ các ca trong bảng; chạy lại những ca liên quan sau khi sửa lỗi hoặc thay đổi mã nguồn có ảnh hưởng.

## 8. Tiến độ dự kiến

| Thời gian | Nội dung |
| --- | --- |
| 26/10/2026 | Rà soát kết quả tuần 3, chốt các tồn tại và phiên bản triển khai. |
| 27/10/2026 – 28/10/2026 | Hoàn thiện backend, giao diện và thực hiện kiểm thử riêng từng phần. |
| 29/10/2026 – 30/10/2026 | Kiểm thử tích hợp, xử lý lỗi và chụp minh chứng. |
| 31/10/2026 | Hoàn thiện báo cáo, tài liệu, ghi nhận chi phí; chạy thử và ghi video demo. |
| 01/11/2026 | Kiểm tra hồ sơ, commit và bàn giao phiên bản tuần 4. |

Thời gian thực hiện thực tế được ghi trong worklog của từng thành viên.

## 9. Cấu trúc lưu trữ

| Nội dung | Vị trí |
| --- | --- |
| Kế hoạch | `TaskAssignments/Week_04.md` |
| Mã nguồn TV1 bổ sung hoặc thay đổi | `code/TanPhat/Week_04/` |
| Mã nguồn TV2 bổ sung hoặc thay đổi | `code/LeHuy/Week_04/` |
| Cấu hình triển khai | `config/TanPhat/Week_04/` và `config/LeHuy/Week_04/` |
| Thiết kế và hướng dẫn triển khai | `design/Week_04/` |
| Kịch bản kiểm thử | `tests/Week_04/` |
| Kết quả kiểm thử | `tests/Week_04/results.md` |
| Minh chứng TV1 | `evidence/TanPhat/Week_04/` |
| Minh chứng TV2 | `evidence/LeHuy/Week_04/` |
| Worklog TV1 | `worklog/TanPhat/Week_04.md` |
| Worklog TV2 | `worklog/LeHuy/Week_04.md` |

Chỉ đưa vào thư mục tuần 4 các tệp cần cho thay đổi và bàn giao tuần này. Với thành phần được giữ nguyên, dẫn chiếu rõ phiên bản kế thừa từ tuần 3.

## 10. Quy định minh chứng

Tên ảnh theo cấu trúc:

`W4-TVx-NN_SS_MoTa.png`

Trong đó:

- `TVx`: thành viên thực hiện.
- `NN`: mã công việc.
- `SS`: thứ tự ảnh.
- `MoTa`: nội dung ảnh.

Ví dụ:

- `W4-TV1-02_01_CommitFailure.png`.
- `W4-TV1-02_02_OrderAfterFailure.png`.
- `W4-TV2-01_01_CustomerCompleted.png`.
- `W4-TV2-01_02_DriverCompleted.png`.
- `W4-TV2-04_01_PollingDisabled.png`.
- `W4-TV2-04_02_ConflictRecovered.png`.

Mỗi ca kiểm thử cần ghi:

- Ngày thực hiện.
- Phiên kiểm thử và mã đơn.
- Điều kiện ban đầu.
- Thao tác thực hiện.
- Kết quả quan sát.
- Kết luận.
- Liên kết minh chứng.

Ảnh phải thể hiện đúng kết quả được mô tả. Che token phiên, callback token và thông tin xác thực trước khi công khai.

## 11. Quản lý phiên bản và chi phí

- Ghi nhận commit của mã nguồn và cấu hình triển khai.
- Các tệp mã nguồn, cấu hình và tài liệu chính có commit riêng; ảnh minh chứng cùng đợt kiểm thử được gom vào một commit chung.
- Không dùng commit tài liệu để thay thế thông tin phiên bản mã đã kiểm thử.
- Ghi số liệu budget theo thời điểm kiểm tra.
- Phân biệt chi phí toàn lab với chi phí riêng của dự án hoặc tuần thực hiện.
- Không suy ra chi phí bằng 0 khi chưa có số liệu đủ chi tiết.
- Ghi giờ làm theo thực tế, không sử dụng thời gian lab tích lũy làm giờ làm của thành viên.
- Giữ tài nguyên phục vụ kiểm thử và bàn giao theo yêu cầu học phần.
- Kết thúc phiên lab khi ngừng làm việc theo hướng dẫn của môi trường; ghi lại trạng thái tài nguyên thực tế.
- Dọn dẹp tài nguyên không còn cần thiết sau khi hoàn tất bàn giao theo yêu cầu học phần, lưu minh chứng trước khi thực hiện.

## 12. Tiêu chí hoàn thành tuần 4

- Luồng nghiệp vụ chính được kiểm thử trên phiên bản triển khai thống nhất.
- Nhánh lỗi commit và callback đến trễ có kết quả đối chiếu.
- Giao diện hiển thị đúng trạng thái timeout và workflow thất bại.
- Cơ chế phục hồi sau CONFLICT được kiểm thử riêng khi tắt polling.
- Có minh chứng truy vết request qua log.
- Kịch bản trình diễn được chạy thử thành công; báo cáo đồ án và video demo không quá 10 phút đã hoàn thiện.
- Mã nguồn, cấu hình, tài liệu và minh chứng thống nhất.
- Worklog có thời gian thực tế, kết quả và commit tương ứng.
- Các tồn tại được ghi rõ cùng ảnh hưởng và hướng xử lý.
- Hồ sơ không chứa token thật hoặc thông tin xác thực AWS.