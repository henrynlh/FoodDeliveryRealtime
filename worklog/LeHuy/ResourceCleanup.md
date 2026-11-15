# NHẬT KÝ DỌN TÀI NGUYÊN AWS SAU BÀN GIAO

- Người thực hiện: Nguyễn Lê Huy — MSSV 24110221.
- Ngày thực hiện: 15/11/2026.
- Tài khoản AWS: `165662523632`.
- Region: `us-east-1` — N. Virginia.
- Căn cứ: yêu cầu của giảng viên về dọn tài nguyên sau demo và bổ sung bằng chứng vào hồ sơ.

## 1. Nội dung thực hiện

Xóa các tài nguyên FoodDeliveryRealtime trên tài khoản sau giai đoạn demo và bàn giao. Với từng dịch vụ, chụp danh sách trước khi xóa và thực hiện xóa rồi tải lại danh sách để đối chiếu kết quả. Các tài nguyên dùng chung của Learner Lab được giữ nguyên.

Đợt dọn này tiếp nối [bản kiểm kê ngày 01/11/2026](../../design/Week_04/resource_inventory.md), khi tài nguyên còn được giữ để phục vụ demo.

## 2. Tài nguyên đã xóa

| Dịch vụ | Tài nguyên đã xóa | Kết quả đối chiếu sau xóa |
|---|---|---|
| Step Functions | `fooddelivery-order-workflow` và workflow thử `fooddelivery-w4-commit-failure-7eedf6c1e5a2` | Danh sách hiển thị State machines (0). |
| API Gateway | WebSocket API `fooddelivery-ws`, ID `lob1j5l21i` | Danh sách hiển thị APIs (0/0). |
| Lambda | Sáu hàm có tiền tố `fooddelivery-`, liệt kê bên dưới | Danh sách từ 11 hàm còn 5 hàm của lab. |
| Amazon SNS | Topic `fooddelivery-order-events` | Danh sách từ 2 topic còn `RedshiftSNS`. |
| DynamoDB | `fooddelivery-orders`, `fooddelivery-connections`, `fooddelivery-workflow-tasks` | Danh sách hiển thị Tables (0). |
| CloudWatch Logs | Sáu log group Lambda của dự án và log group API Gateway | Danh sách từ 11 log group còn 4 mục được giữ lại. |
| Amazon S3 | Bucket `fooddelivery-web` | Danh sách General purpose buckets hiển thị (0). |

### Sáu Lambda đã xóa

- `fooddelivery-prepare-task`
- `fooddelivery-submit-transition`
- `fooddelivery-commit-transition`
- `fooddelivery-ws-dispatcher`
- `fooddelivery-broadcast`
- `fooddelivery-ws-foundation`

### Bảy log group đã xóa

- `/aws/lambda/fooddelivery-prepare-task`
- `/aws/lambda/fooddelivery-submit-transition`
- `/aws/lambda/fooddelivery-commit-transition`
- `/aws/lambda/fooddelivery-ws-dispatcher`
- `/aws/lambda/fooddelivery-broadcast`
- `/aws/lambda/fooddelivery-ws-foundation`
- `/aws/apigateway/lob1j5l21i/dev`

## 3. Tài nguyên được giữ lại

### Lambda của Learner Lab

- `MainMonitoringFunction`
- `ModLabRole`
- `RedshiftEventSubscription`
- `RedshiftOverwatch`
- `RoleCreationFunction`

### SNS và CloudWatch Logs

- Giữ topic `RedshiftSNS`.
- Giữ log group `/aws/apigateway/welcome`.
- Giữ log group `/aws/lambda/RedshiftEventSubscription`.
- Giữ log group `/aws/lambda/RedshiftOverwatch`.
- Giữ log group `/aws/lambda/RoleCreationFunction`.

## 4. Minh chứng trước và sau khi dọn

| Hạng mục | Trước khi xóa | Sau khi xóa |
|---|---|---|
| Step Functions | [Hai workflow của dự án](../../evidence/LeHuy/ResourceCleanup/01_StepFunctions_Before.png) | [Không còn state machine](../../evidence/LeHuy/ResourceCleanup/02_StepFunctions_After.png) |
| API Gateway | [WebSocket API fooddelivery-ws](../../evidence/LeHuy/ResourceCleanup/03_ApiGateway_Before.png) | [Không còn API](../../evidence/LeHuy/ResourceCleanup/04_ApiGateway_After.png) |
| Lambda | [Danh sách 11 hàm](../../evidence/LeHuy/ResourceCleanup/05_Lambda_Before.png) | [Còn 5 hàm của lab](../../evidence/LeHuy/ResourceCleanup/06_Lambda_After.png) |
| SNS | [Hai topic trước xóa](../../evidence/LeHuy/ResourceCleanup/07_Sns_Before.png) | [Giữ lại RedshiftSNS](../../evidence/LeHuy/ResourceCleanup/08_Sns_After.png) |
| DynamoDB | [Ba bảng dự án](../../evidence/LeHuy/ResourceCleanup/09_DynamoDB_Before.png) | [Không còn bảng](../../evidence/LeHuy/ResourceCleanup/10_DynamoDB_After.png) |
| CloudWatch Logs | [Danh sách 11 log group](../../evidence/LeHuy/ResourceCleanup/11_CloudWatch_Before.png) | [Còn 4 log group được giữ lại](../../evidence/LeHuy/ResourceCleanup/12_CloudWatch_After.png) |
| S3 | [Bucket fooddelivery-web](../../evidence/LeHuy/ResourceCleanup/13_S3_Before.png) | [Không còn general purpose bucket](../../evidence/LeHuy/ResourceCleanup/14_S3_After.png) |

- [Default VPC được giữ nguyên](../../evidence/LeHuy/ResourceCleanup/15_VPC_DefaultRetained.png).

