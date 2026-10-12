# Nhật ký làm việc tuần 1: 
Người thực hiện: Nguyễn Lê Huy – 24110221.

Thời gian thực hiện: 8-10 tiếng

## Tạo bảng Orders
- Ngày thực hiện: 07/10/2026.
- Region: us-east-1.
- Công việc: Tạo bảng fooddelivery-orders.
- Partition key: orderId, kiểu String.
- Capacity mode: On-demand.
- Kết quả: ACTIVE.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
### Minh chứng:
- [Thông tin bảng Orders](../../evidence/LeHuy/Week_01/E-TV2-01_Orders_Overview.png)
- [Tag của bảng Orders](../../evidence/LeHuy/Week_01/E-TV2-02_Orders_Tags.png)

## Kiểm thử dữ liệu Orders
- Tạo bản ghi TEST-W1-TV2: Thành công.
- Query bằng orderId: Tìm thấy đúng bản ghi TEST-W1-TV2.
- Kiểm tra status và kiểu dữ liệu version: status là PLACED. version là Number, giá trị 1.
- Xóa bản ghi thử và Query lại: Query lại không tìm thấy bản ghi TEST-W1-TV2.
### Minh chứng:
- [Đọc đơn hàng mẫu](../../evidence/LeHuy/Week_01/E-TV2-03_Orders_ReadTest.png)
- [Kiểm tra xóa đơn mẫu](../../evidence/LeHuy/Week_01/E-TV2-04_Orders_DeleteTest.png)

## Dựng bảng Connections
- Ngày thực hiện: 07/10/2026.
- Region: us-east-1.
- Tên bảng: fooddelivery-connections.
- Partition key: connectionId, kiểu String.
- Capacity mode: On-demand.
- Trạng thái bảng: Active.
- Chỉ mục ByOrderId: partition key orderId, kiểu String. Projection ALL.
- Trạng thái chỉ mục: Active.
- TTL: Enabled, thuộc tính expiresAt.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
### Minh chứng
- [Thông tin bảng](../../evidence/LeHuy/Week_01/E-TV2-05_Connections_Overview.png)
- [Tag của bảng](../../evidence/LeHuy/Week_01/E-TV2-06_Connections_Tags.png)
- [Chỉ mục ByOrderId](../../evidence/LeHuy/Week_01/E-TV2-07_Connections_ByOrderId.png)
- [Cấu hình TTL](../../evidence/LeHuy/Week_01/E-TV2-08_Connections_TTL.png)

## Dựng bảng WorkflowTasks
- Ngày thực hiện: 07/10/2026.
- Region: us-east-1.
- Tên bảng: fooddelivery-workflow-tasks.
- Partition key: orderId, kiểu String.
- Sort key: step, kiểu String.
- Capacity mode: On-demand.
- Trạng thái bảng: Active.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Mục đích: Chuẩn bị nơi lưu thông tin các bước chờ callback của Step Functions.
- Phạm vi hoàn thành: Đã dựng cấu trúc bảng. Chưa kiểm thử callback nghiệp vụ.
### Minh chứng
- [Thông tin bảng](../../evidence/LeHuy/Week_01/E-TV2-09_WorkflowTasks_Overview.png)
- [Tag của bảng](../../evidence/LeHuy/Week_01/E-TV2-10_WorkflowTasks_Tags.png)

## Dựng nền tảng S3
- Ngày thực hiện: 09/10/2026.
- Region: us-east-1.
- Tên bucket: fooddelivery-web.
- Mục đích: lưu các tệp giao diện web của đồ án.
- Object Ownership: Bucket owner enforced, ACLs disabled.
- Block all public access: On.
- Default encryption: SSE-S3.
- Versioning: Disabled.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Đã tải lên object: index.html.
- Kiểm tra: tải index.html xuống và mở bằng trình duyệt thành công.
### Minh chứng
- [Thông tin bucket](../../evidence/LeHuy/Week_01/E-TV2-11_S3_Overview.png)
- [Tag của bucket](../../evidence/LeHuy/Week_01/E-TV2-12_S3_Tags.png)
- [Quyền truy cập](../../evidence/LeHuy/Week_01/E-TV2-13_S3_BlockPublicAccess.png)
- [Tệp đã tải lên](../../evidence/LeHuy/Week_01/E-TV2-14_S3_IndexUpload.png)

## Dựng và kiểm thử Lambda nền tảng
- Ngày thực hiện: 09/10/2026.
- Region: us-east-1.
- Tên hàm: fooddelivery-ws-foundation.
- Runtime: Python 3.13.
- Handler: lambda_function.lambda_handler.
- Execution role: LabRole.
- Memory: 128 MB.
- Timeout: 10 giây.
- Biến môi trường CONNECTIONS_TABLE: fooddelivery-connections.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Kiểm thử test_connect: trả về 200, Connected.
- Kiểm tra DynamoDB: tìm thấy bản ghi MANUAL-W1-TV2.
- Kiểm thử test_disconnect: trả về 200, Disconnected.
- Query lại: không còn bản ghi MANUAL-W1-TV2.
- Phạm vi kiểm thử: sự kiện mô phỏng trong Lambda Console.
- Phạm vi của bước này: kiểm thử bằng sự kiện mô phỏng trong Lambda Console.
- Kiểm thử WebSocket thực tế được ghi tại mục tiếp theo
### Minh chứng
- [Cấu hình Lambda](../../evidence/LeHuy/Week_01/E-TV2-15_Lambda_Config.png)
- [Execution role LabRole](../../evidence/LeHuy/Week_01/E-TV2-16_Lambda_LabRole.png)
- [Biến môi trường CONNECTIONS_TABLE](../../evidence/LeHuy/Week_01/E-TV2-17_Lambda_Environment.png)
- [Tag của Lambda](../../evidence/LeHuy/Week_01/E-TV2-18_Lambda_Tags.png)
- [Kết quả test_connect](../../evidence/LeHuy/Week_01/E-TV2-19_Lambda_ConnectTest.png)
- [Bản ghi MANUAL-W1-TV2 trong DynamoDB](../../evidence/LeHuy/Week_01/E-TV2-20_Connections_TestItem.png)
- [Kết quả test_disconnect](../../evidence/LeHuy/Week_01/E-TV2-21_Lambda_DisconnectTest.png)
- [Query xác nhận bản ghi đã bị xóa](../../evidence/LeHuy/Week_01/E-TV2-22_Connections_AfterDisconnect.png)

## Dựng và kiểm thử API Gateway WebSocket
- Ngày thực hiện: 09/10/2026.
- Region: us-east-1.
- Tên API: fooddelivery-ws.
- Loại API: WebSocket.
- Route selection expression: $request.body.action.
- Routes: $connect, $disconnect, $default.
- Lambda tích hợp cho cả ba route: fooddelivery-ws-foundation.
- Stage triển khai: dev.
- WebSocket URL: wss://lob1j5l21i.execute-api.us-east-1.amazonaws.com/dev/
- Authorization: NONE, dùng kiểm thử nền tảng tuần 1.
- Tag Project: FoodDeliveryRealtime.
- Tag Owner: 24110221.
- Công cụ kiểm thử: code/test_websocket.html.
- Kết nối: trình duyệt hiển thị OPEN.
- Kiểm tra DynamoDB: xuất hiện bản ghi connectionId do AWS tạo.
- Gửi ping: nhận phản hồi có ok = true và message = pong.
- Ngắt kết nối: trình duyệt hiển thị CLOSED.
- Query lại connectionId: không còn bản ghi.
- Phạm vi hoàn thành: kiểm thử kết nối, gửi nhận tin nhắn và dọn bản ghi kết nối.
- Chưa triển khai chức năng đặt hàng, cập nhật trạng thái đơn và xác thực người dùng.
### Minh chứng
- [Các route và tích hợp Lambda](../../evidence/LeHuy/Week_01/E-TV2-23_WebSocket_Routes.png)
- [Stage dev và WebSocket URL](../../evidence/LeHuy/Week_01/E-TV2-24_WebSocket_Stage.png)
- [Tag của API](../../evidence/LeHuy/Week_01/E-TV2-25_WebSocket_Tags.png)
- [Kết nối thành công](../../evidence/LeHuy/Week_01/E-TV2-26_WebSocket_Connected.png)
- [Bản ghi kết nối thật](../../evidence/LeHuy/Week_01/E-TV2-27_WebSocket_ConnectionItem.png)
- [Gửi ping và nhận pong](../../evidence/LeHuy/Week_01/E-TV2-28_WebSocket_Pong.png)
- [Ngắt kết nối](../../evidence/LeHuy/Week_01/E-TV2-29_WebSocket_Closed.png)
- [Kiểm tra bản ghi đã được xóa](../../evidence/LeHuy/Week_01/E-TV2-30_WebSocket_AfterDisconnect.png)