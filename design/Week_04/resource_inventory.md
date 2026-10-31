# KIỂM KÊ TÀI NGUYÊN PHỤC VỤ DEMO VÀ BÀN GIAO

- Ngày kiểm kê: 01/11/2026.
- Người thực hiện: Nguyễn Lê Huy — TV2 — 24110221.
- AWS Account ID: 165662523632.
- Region: us-east-1.
- Phạm vi: các thành phần ứng dụng đã đối chiếu qua AWS Console, chưa phải toàn bộ tài nguyên của tài khoản.

## 1. Tài nguyên đã đối chiếu

| Dịch vụ | Tài nguyên | Kết quả quan sát | Phương án hiện tại |
|---|---|---|---|
| Lambda | fooddelivery-prepare-task | Có trong danh sách hàm | Giữ phục vụ workflow. |
| Lambda | fooddelivery-submit-transition | Có trong danh sách hàm | Giữ phục vụ cập nhật đơn. |
| Lambda | fooddelivery-commit-transition | Có trong danh sách hàm | Giữ phục vụ ghi nhận chuyển trạng thái. |
| Lambda | fooddelivery-ws-dispatcher | Có trong danh sách hàm | Giữ phục vụ giao diện WebSocket. |
| Lambda | fooddelivery-broadcast | Có trong danh sách hàm | Giữ phục vụ gửi cập nhật. |
| Lambda | fooddelivery-ws-foundation | Có trong danh sách hàm | Tạm giữ thành phần nền tảng tuần 1. Rà soát phụ thuộc trước khi cân nhắc dọn dẹp. |
| DynamoDB | fooddelivery-orders | Active, On-demand. Khóa orderId. | Giữ dữ liệu kiểm thử và demo. |
| DynamoDB | fooddelivery-workflow-tasks | Active, On-demand. Khóa orderId và step. | Giữ phục vụ workflow và đối chiếu. |
| DynamoDB | fooddelivery-connections | Active, On-demand. Khóa connectionId. | Giữ phục vụ kết nối WebSocket. |
| Step Functions | fooddelivery-order-workflow | Standard, Active | Giữ phục vụ demo và bàn giao. |
| API Gateway | fooddelivery-ws | WebSocket, Regional | Giữ phục vụ kết nối giao diện. |
| SNS | fooddelivery-order-events | Standard | Giữ phục vụ thông báo. Chưa đối chiếu subscription trong đợt kiểm kê này. |

## 2. Ngân sách

- Learner Lab hiển thị Used $0 of $50 tại thời điểm chụp.
- Đây là số liệu ngân sách toàn lab đang hiển thị, chưa tách riêng dự án hoặc tuần 4.
- Không kết luận chi phí thực tế của dự án bằng 0 từ số liệu này.

## 3. Phương án giữ và dọn dẹp

- Giữ các thành phần ứng dụng trong thời gian quay demo và chờ bàn giao.
- Giữ dữ liệu, lịch sử execution và nhật ký cần đối chiếu kết quả kiểm thử.
- Chưa thực hiện xóa tài nguyên trong đợt kiểm kê này.
- Chỉ dọn dẹp sau khi hoàn thành bàn giao và theo yêu cầu học phần.
- Trước khi dọn dẹp, lưu cấu hình và minh chứng cần thiết, kiểm tra phụ thuộc và xác định đúng tài khoản, region, tài nguyên.
- VPC, S3, IAM và các thành phần khác chưa được kiểm kê lại trong bộ ảnh này. Không suy luận chúng không tồn tại.

## 4. Minh chứng

- [Ngân sách lab](../../evidence/LeHuy/Week_04/W4-TV2-07_01_LabBudget.png).
- [Danh sách Lambda](../../evidence/LeHuy/Week_04/W4-TV2-07_02_LambdaInventory.png).
- [Danh sách DynamoDB](../../evidence/LeHuy/Week_04/W4-TV2-07_03_DynamoDBInventory.png).
- [Danh sách workflow](../../evidence/LeHuy/Week_04/W4-TV2-07_04_WorkflowInventory.png).
- [API Gateway](../../evidence/LeHuy/Week_04/W4-TV2-07_05_ApiGatewayInventory.png).
- [SNS topic](../../evidence/LeHuy/Week_04/W4-TV2-07_06_SnsInventory.png).