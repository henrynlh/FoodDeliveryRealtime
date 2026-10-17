# KẾ HOẠCH CÔNG VIỆC TUẦN 3 – FOODDELIVERYREALTIME

- **Đề tài:** Ứng dụng giao đồ ăn – Theo dõi trạng thái thời gian thực.
- **Thời gian dự kiến:** 19/10/2026 – 25/10/2026.
- **TV1:** Trương Tấn Phát – MSSV 24110298.
- **TV2:** Nguyễn Lê Huy – MSSV 24110221.
- **Repository:** https://github.com/henrynlh/FoodDeliveryRealtime
- **Môi trường tích hợp:** AWS `us-east-1`, sử dụng tài nguyên trong tài khoản tích hợp của Huy.
- **Trạng thái:** Kế hoạch dự kiến. Chỉ cập nhật hoàn thành khi có kết quả thực tế và minh chứng.

## 1. Cơ sở triển khai

Theo worklog tuần 2, luồng `PLACED → ACCEPTED → DELIVERING → COMPLETED` đã chạy thành công trên môi trường tích hợp với Step Functions, các Lambda Prepare/Submit/Commit và SNS. Giao diện khách hàng và tài xế đã thực hiện được luồng cơ bản qua WebSocket và nhận `ORDER_UPDATED` sau các bước commit.

Đã kiểm thử gửi lặp yêu cầu tạo đơn, phân quyền đọc/theo dõi đơn bằng phiên demo, kết nối lại và đăng ký theo dõi lại bằng thao tác thủ công. Chưa kiểm chứng tự động khôi phục khi mất mạng. Lần thử hai tài xế nhận cùng đơn chưa đủ yêu cầu và phản hồi của cả hai phiên để kết luận xử lý cạnh tranh đúng.

Một số Lambda đã được chỉnh trên AWS khi tích hợp nhưng chưa có đầy đủ bản mã tương ứng trong Git. Đầu tuần 3 cần đối chiếu và đồng bộ bản đang chạy trước khi tiếp tục sửa. Phiên demo hiện tại chưa phải hệ thống xác thực người dùng hoàn chỉnh.

## 2. Mục tiêu và phạm vi

- Hoàn thiện tích hợp xuyên suốt từ giao diện đến WebSocket, workflow, DynamoDB và thông báo.
- Kiểm soát yêu cầu trùng, version cũ, chuyển trạng thái sai và tranh nhận đơn.
- Tự động kết nối lại sau mất mạng, khôi phục theo dõi đơn và lấy trạng thái mới nhất từ backend.
- Rà soát phân quyền nghiệp vụ, quyền AWS thực tế của `LabRole` và log CloudWatch.
- Bàn giao mã nguồn khớp môi trường đang chạy, tài liệu cấu hình và kết quả kiểm thử có thể đối chiếu.

Tuần 3 tiếp tục sử dụng phiên demo do backend quản lý. Các thay đổi về xác thực đầy đủ, hosting hoặc IaC toàn bộ không thuộc tiêu chí bắt buộc của tuần này. Ưu tiên script hoặc hướng dẫn có thể lặp lại cho cấu hình đang sử dụng; ghi rõ thao tác còn thủ công.

## 3. Phân công nhiệm vụ

### 3.1. TV1 – Trương Tấn Phát

| Mã | Công việc | Nội dung và tiêu chí bàn giao | Dự kiến |
|---|---|---|---|
| W3-TV1-01 | Đồng bộ backend và hợp đồng dữ liệu | Phối hợp Huy lấy bản Prepare/Submit/Commit và ASL đang chạy; rà soát trước khi lưu vào Git. Thống nhất `requestId`, `expectedVersion`, `actorId`, phản hồi thành công/lỗi và các trường trạng thái. | 2 giờ |
| W3-TV1-02 | Yêu cầu trùng và cạnh tranh | Xử lý gửi lại cùng yêu cầu chuyển trạng thái; không tăng version hoặc commit thêm cho cùng thao tác. Kiểm tra claim/cập nhật có điều kiện để chỉ một tài xế thắng khi tranh nhận đơn. Ghi rõ chính sách phát lại thông báo. | 2 giờ |
| W3-TV1-03 | Yêu cầu không hợp lệ và callback | Từ chối version cũ, chuyển sai thứ tự, cập nhật sau hoàn tất; kiểm tra callback sai, gửi lại và timeout. Không commit thành công khi callback thất bại. Chuẩn hóa lỗi cho frontend. | 2 giờ |
| W3-TV1-04 | Quyền AWS và log backend | Kiểm tra quyền thực tế của `LabRole` cho Lambda, Step Functions, DynamoDB, SNS và CloudWatch theo thao tác cần dùng. Bổ sung log theo `orderId`, `requestId`, trạng thái/version khi có; không ghi token phiên hay task token vào log. | 2 giờ |
| W3-TV1-05 | Hướng dẫn triển khai backend | Ghi runtime, handler, biến môi trường, ARN cần thay và thứ tự triển khai. Bổ sung script kiểm tra cấu hình nếu phù hợp; không kèm khóa truy cập hoặc token. | 1 giờ |
| W3-TV1-06 | Kiểm thử tích hợp và sửa lỗi | Cùng Huy chạy các ca bên dưới, đối chiếu Orders, WorkflowTasks, execution và SNS. Lưu request/response của ca cạnh tranh; sửa lỗi thuộc workflow và Lambda nghiệp vụ. | 3 giờ |
| W3-TV1-07 | Tài liệu và worklog | Hoàn thiện kết quả backend, liên kết minh chứng/commit, ghi thời gian thực tế, giới hạn môi trường và lỗi còn tồn tại. | 2 giờ |
| W3-TV1-08 | Dự phòng | Dành cho lỗi tích hợp hoặc chạy lại ca thất bại; ghi thời gian thực dùng vào worklog. | 2 giờ |
| | **Tổng dự kiến, gồm dự phòng** | | **16 giờ** |

### 3.2. TV2 – Nguyễn Lê Huy

| Mã | Công việc | Nội dung và tiêu chí bàn giao | Dự kiến |
|---|---|---|---|
| W3-TV2-01 | Đồng bộ dispatcher và broadcast | Lưu bản dispatcher/broadcast đang chạy vào Git, đối chiếu cấu hình và giao tiếp với TV1. Hiển thị lỗi backend theo hợp đồng thống nhất; lấy lại dữ liệu khi có xung đột. | 2 giờ |
| W3-TV2-02 | Hoàn thiện hai giao diện | Hiển thị mã đơn, tiến trình, dữ liệu trống/đang tải/lỗi. Tài xế phân biệt đơn có thể nhận và đơn phụ trách; chỉ bật nút đúng bước, khóa khi đang gửi và mở lại khi có kết quả/lỗi. | 2 giờ |
| W3-TV2-03 | Khôi phục sau mất kết nối | Tự kết nối lại với thời gian chờ tăng dần có giới hạn; không tự nối lại sau khi người dùng chủ động ngắt. Sau OPEN, đăng ký theo dõi lại và lấy snapshot mới. Giữ mã đơn qua tải lại trang, nhập lại token khi cần; không lưu token vào URL chia sẻ hoặc bộ nhớ trình duyệt lâu dài. | 3 giờ |
| W3-TV2-04 | Đồng bộ version và phân quyền | Bỏ qua snapshot/sự kiện version cũ, xử lý sự kiện trùng mà không lùi trạng thái. Kiểm thử quyền ở dispatcher và broadcast để khách/tài xế khác không đọc, theo dõi hoặc nhận dữ liệu trái phép. | 2 giờ |
| W3-TV2-05 | Giám sát và cấu hình tích hợp | Kiểm tra log API Gateway WebSocket nếu môi trường cho phép và log Lambda dispatcher/broadcast. Lưu cách tra lỗi kết nối, gửi tin thất bại, kết nối đã đóng; ghi cấu hình/retention hiện có và đề xuất điều chỉnh trong quyền lab. | 1 giờ |
| W3-TV2-06 | Kiểm thử tích hợp và minh chứng | Cùng Phát chạy các ca bên dưới; lưu nhật ký hai phía và ảnh giao diện, đối chiếu với dữ liệu AWS. Sửa lỗi frontend, dispatcher/broadcast thuộc phần phụ trách. | 2 giờ |
| W3-TV2-07 | Tài liệu và worklog | Tổng hợp kết quả chung, hướng dẫn cấu hình và chạy giao diện; kiểm tra đường dẫn minh chứng, SHA, liên kết GitHub và ghi thời gian thực tế. | 2 giờ |
| W3-TV2-08 | Dự phòng | Dành cho lỗi tích hợp, reconnect hoặc kiểm thử lại; ghi thời gian thực dùng vào worklog. | 2 giờ |
| | **Tổng dự kiến, gồm dự phòng** | | **16 giờ** |

TV1 chịu trách nhiệm chính về workflow và Lambda nghiệp vụ; TV2 chịu trách nhiệm chính về frontend, dispatcher, broadcast và môi trường tích hợp. Khi triển khai lên tài khoản tích hợp, hai thành viên thống nhất phiên bản trước khi cập nhật để tránh ghi đè thay đổi của nhau.

## 4. Kịch bản kiểm thử và tiêu chí đạt

Các mã dưới đây dành riêng cho tuần 3. Với mỗi ca, lưu thời điểm, dữ liệu đầu vào, kết quả mong đợi/thực tế, người thực hiện và đường dẫn minh chứng. Trạng thái kết quả gồm **Chưa chạy / Đạt / Không đạt / Bị chặn**; không coi ca chưa chạy hoặc bị chặn là đạt.

| Mã | Kịch bản | Tiêu chí đạt | Phụ trách chính |
|---|---|---|---|
| W3-TC01 | Luồng tạo đơn đến hoàn tất từ hai giao diện | Trạng thái lần lượt PLACED, ACCEPTED, DELIVERING, COMPLETED; version 1–4 trên đơn mới. Orders, giao diện và execution cuối thống nhất; đối chiếu SNS theo cấu hình. | Cả hai |
| W3-TC02 | Gửi lại cùng requestId khi chuyển trạng thái | Không commit hoặc tăng version thêm cho cùng thao tác; phản hồi theo hợp đồng. Kiểm tra tác động SNS/broadcast và ghi rõ nếu nhận thông điệp trùng. | TV1 |
| W3-TC03 | Yêu cầu với version cũ | Backend từ chối, dữ liệu không bị ghi đè; frontend báo lỗi và tải lại snapshot hiện tại. | Cả hai |
| W3-TC04 | Chuyển sai thứ tự hoặc cập nhật đơn hoàn tất | Từ chối yêu cầu; status, version và tài xế được giao không bị thay đổi sai. | TV1 |
| W3-TC05 | Callback sai hoặc gửi lại | Không commit thêm hoặc chuyển sai trạng thái. Ghi rõ lỗi tại Lambda/API và trạng thái execution; callback sai có thể để workflow tiếp tục chờ đến timeout. | TV1 |
| W3-TC06 | Hết thời hạn chờ callback | Workflow đi vào nhánh timeout đã thiết kế; Orders không tự chuyển thành COMPLETED. Đối chiếu workflowStatus theo quy ước đã thống nhất. | TV1 |
| W3-TC07 | Mất mạng khi đơn đổi trạng thái rồi có mạng lại | Tự kết nối lại, đăng ký theo dõi lại và hiển thị snapshot mới nhất; tiếp tục nhận ORDER_UPDATED. Chủ động ngắt thì không tự kết nối lại. | TV2 |
| W3-TC08 | Tải lại trang khi đang theo dõi đơn | Khôi phục mã đơn; sau khi có phiên hợp lệ, kết nối và theo dõi lại đúng đơn, tải trạng thái hiện tại. Không khôi phục dữ liệu của phiên khác trái phép. | TV2 |
| W3-TC09 | Nhận sự kiện trùng hoặc version cũ | Giao diện không lùi trạng thái và không tạo thao tác nghiệp vụ mới do sự kiện trùng. Ghi cách mô phỏng sự kiện. | TV2 |
| W3-TC10 | Bấm nhanh nhiều lần vào nút chuyển trạng thái | Khóa thao tác trong khi chờ; mở lại phù hợp sau thành công/lỗi. Backend vẫn kiểm soát yêu cầu lặp dù bỏ qua giao diện. | Cả hai |
| W3-TC11 | Hồi quy phân quyền | C002 và D002 không đọc/theo dõi/cập nhật đơn ngoài quyền; không nhận broadcast sau khi quyền truy cập không còn phù hợp. Phiên thiếu hoặc sai token bị từ chối. | TV2 |
| W3-TC12 | Hai tài xế tranh nhận cùng đơn | Gửi hai yêu cầu gần như đồng thời, lưu requestId, thời điểm và phản hồi cả hai phía; chỉ một tài xế nhận được đơn. Orders chỉ có một driverId, version tăng một lần cho bước nhận đơn. Dùng script nếu nút giao diện không tạo được cạnh tranh. | TV1, TV2 hỗ trợ |
| W3-TC13 | Tra lỗi qua CloudWatch và kiểm tra quyền AWS | Theo dấu được một đơn/yêu cầu qua các Lambda và execution; các thao tác cần thiết hoạt động với role hiện tại. Ghi quyền hoặc chức năng giám sát bị lab hạn chế, không đưa token vào log. | Cả hai |

Với thông báo, tách biệt việc commit trạng thái một lần và việc phân phối thông điệp. Nếu có thông điệp trùng, ghi nhận thực tế và kiểm tra frontend xử lý đúng; không kết luận mọi thông báo được giao đúng một lần chỉ từ một lần thử.

## 5. Lịch và mốc bàn giao dự kiến

| Thời gian | TV1 – Trương Tấn Phát | TV2 – Nguyễn Lê Huy | Mốc chung |
|---|---|---|---|
| 19/10 | Đối chiếu bản Lambda/ASL; thống nhất lỗi và dữ liệu. | Đồng bộ dispatcher/broadcast; rà soát frontend. | Chốt phiên bản nền và hợp đồng dữ liệu. |
| 20/10 – 22/10 | Hoàn thiện yêu cầu trùng, cạnh tranh, callback và log. | Hoàn thiện giao diện, reconnect, version và log kết nối. | Có bản tích hợp để chạy thử. |
| 23/10 | Triển khai backend phối hợp, rà soát quyền và hướng dẫn cấu hình. | Triển khai phần WebSocket, kiểm tra CloudWatch và cấu hình môi trường. | Chốt bản kiểm thử và lưu commit tương ứng. |
| 24/10 | Chạy ca backend/cạnh tranh; sửa lỗi và lưu minh chứng. | Chạy ca giao diện/reconnect/phân quyền; lưu minh chứng. | Cập nhật kết quả từng ca, đối chiếu luồng E2E. |
| 25/10 | Chạy lại ca liên quan sau sửa lỗi, hoàn thiện worklog. | Tổng hợp kết quả, kiểm tra link và hướng dẫn chạy demo. | Bàn giao mã, cấu hình và danh sách lỗi còn lại. |

Nếu thay đổi hợp đồng dữ liệu hoặc cấu hình ảnh hưởng thành viên còn lại, cập nhật tài liệu và thông báo trước khi triển khai. Ưu tiên xử lý lỗi mất dữ liệu, sai phân quyền, sai chuyển trạng thái và không khôi phục được kết nối trước phần trình bày giao diện.

## 6. Sản phẩm và vị trí bàn giao

Các đường dẫn tuần 3 dưới đây là vị trí dự kiến; tạo khi triển khai, chưa phải các tệp đã hoàn thành. Giữ bản tuần 2 làm mốc đối chiếu.

| Sản phẩm | Vị trí dự kiến | Phụ trách |
|---|---|---|
| Prepare/Submit/Commit đã rà soát | `code/TanPhat/Week_03/` | TV1 |
| ASL nghiệp vụ và cấu hình backend | `config/TanPhat/Week_03/` | TV1 |
| customer.html, driver.html, shared.js, dispatcher và broadcast | `code/LeHuy/Week_03/` | TV2 |
| ASL realtime và cấu hình tích hợp đã loại token | `config/LeHuy/Week_03/` | TV2 |
| Hợp đồng request/response, dữ liệu và mã lỗi | `design/Week_03/api_contract.md` | TV1 soạn, TV2 đối chiếu |
| Hướng dẫn cấu hình, triển khai, quyền và tra log | `design/Week_03/deployment.md` | Cả hai |
| Kịch bản và kết quả chung W3-TC01–W3-TC13 | `tests/Week_03/results.md` | Cả hai, TV2 tổng hợp |
| Script mô phỏng cạnh tranh/sự kiện hoặc kiểm tra cấu hình, nếu cần | `tests/Week_03/` hoặc `scripts/Week_03/` | Thành viên phụ trách ca |
| Log đã loại thông tin nhạy cảm, ảnh và dữ liệu đối chiếu | `evidence/TanPhat/Week_03/`, `evidence/LeHuy/Week_03/` | Mỗi người lưu phần mình |
| Công việc, thời gian thực tế và liên kết commit | `worklog/TanPhat/Week_03.md`, `worklog/LeHuy/Week_03.md` | Mỗi người cập nhật |

Minh chứng cần thể hiện đầu vào và kết quả, không chỉ ảnh cấu hình. Riêng ca cạnh tranh phải có cả hai yêu cầu/phản hồi và dữ liệu cuối; riêng reconnect phải có thời điểm mất mạng, khôi phục kết nối, snapshot và thông điệp mới sau khôi phục.

Mã nguồn/cấu hình bàn giao phải khớp bản đã kiểm thử trên AWS. Tệp phiên demo vẫn dùng hậu tố `.local.json` và được bỏ qua bởi Git; không đưa token, task token hoặc thông tin đăng nhập vào mã, log hay ảnh minh chứng. Ghi lại phần thiết lập còn thủ công và giới hạn Learner Lab; không tự đặt mục tiêu thay policy của `LabRole` nếu tài khoản không cho phép.

## 7. Điều kiện hoàn thành tuần 3

- [ ] Mã nguồn và cấu hình trong Git khớp phiên bản chạy trên môi trường tích hợp.
- [ ] Hợp đồng dữ liệu, phản hồi lỗi và trách nhiệm hai thành viên đã thống nhất.
- [ ] Luồng E2E hoạt động; Orders, giao diện và execution cuối thống nhất.
- [ ] Yêu cầu trùng, version cũ, callback/timeout và tranh nhận đơn có kết quả kiểm tra.
- [ ] Reconnect tự động, tải lại trang và theo dõi lại đơn được kiểm chứng.
- [ ] Phân quyền ở backend và broadcast được kiểm thử, không chỉ dựa vào khóa nút giao diện.
- [ ] Quyền AWS và log CloudWatch đã được rà soát; hạn chế của lab được ghi rõ.
- [ ] W3-TC01–W3-TC13 có trạng thái thực tế, minh chứng và phiên bản mã được kiểm thử. Ca không đạt/bị chặn có lý do, người xử lý và hướng giải quyết; không ghi hoàn thành đầy đủ khi còn tiêu chí bắt buộc chưa đạt.
- [ ] Mã nguồn, tài liệu và minh chứng đã được đẩy lên GitHub; liên kết truy cập được.
- [ ] Worklog ghi công việc, thời gian thực tế và phần hỗ trợ của AI nếu có.
- [ ] Ghi trạng thái tài nguyên, cấu hình log và chi phí đã kiểm tra; chưa có số liệu thì ghi chưa xác nhận.
