# Nhật kí làm việc tuần 1:
Người thực hiện: Trương Tấn Phát - 24110298

Thời gian thực hiện: 6-7 tiếng


## Dựng VPC
- Ngày thực hiện: 9/10/2026
- Region: us-east-1.
- VPC: fooddelivery-vpc; CIDR 10.20.0.0/16
- Subnet-a: 10.20.1.0/24; AZ: use1-az4 (us-east-1a)
- Subnet-b: 10.20.2.0/24; AZ: use1-az6 (us-east-1b)
- Route table: fooddelivery-rt-main
- Route và liên kết subnet: Đã kết nối thành công.
- Tag Project: FoodDeliveryRealtime. Tag Owner: 24110298.
- Không tạo IGW, NAT hoặc EC2. Lambda thử chạy ngoài VPC.
- Kết quả: Đạt.

### Minh chứng
- [VPC ID, tên, CIDR và trạng thái.](../../evidence/TanPhat/Week_01/E-TV1-03_VPC_Overview.png)
- [Tag Project và Owner của VPC.](../../evidence/TanPhat/Week_01/E-TV1-04_VPC_Tags.png)
- [Tên, VPC ID, CIDR, AZ và tag của subnet-a.](../../evidence/TanPhat/Week_01/E-TV1-05_SubnetA.png)
- [Tên, VPC ID, CIDR, AZ và tag của subnet-b.](../../evidence/TanPhat/Week_01/E-TV1-06_SubnetB.png)
- [Tên bảng route, VPC ID và route local.](../../evidence/TanPhat/Week_01/E-TV1-07_RouteTable_Associations.png)
- [Tags và liên kết subnet. Nếu không vừa, dùng ảnh bổ sung _02.](../../evidence/TanPhat/Week_01/E-TV1-08_RouteTable_Tags.png)

## Dựng SNS và kiểm thử email
- Ngày thực hiện: 9/10/2026.
- Region: us-east-1.
- Topic: fooddelivery-order-events. Type: Standard.
- Topic ARN: arn:aws:sns:us-east-1:053151184394:fooddelivery-order-events.
- Subscription: Email; trạng thái: Confirmed.
- Tag Project: FoodDeliveryRealtime. Tag Owner: 24110298.
- Email nhận được: Có.
- Phạm vi: email kỹ thuật tuần 1, chưa gắn mốc nghiệp vụ.

### Minh chứng
- [Tên topic, Standard và Topic ARN.](../../evidence/TanPhat/Week_01/E-TV1-09_SNS_Topic.png)
- [Project và Owner.](../../evidence/TanPhat/Week_01/E-TV1-10_SNS_Tags.png)
- [Email subscription đã xác nhận, không PendingConfirmation.](../../evidence/TanPhat/Week_01/E-TV1-11_SNS_Subscription.png)
- [Email có subject và nội dung bài thử. Không chụp link xác nhận.](../../evidence/TanPhat/Week_01/E-TV1-12_SNS_ConsoleEmail.png)

## Dựng Lambda nền tảng TV1
- Ngày thực hiện: 9/10/2026.
- Region: us-east-1.
- Function: fooddelivery-foundation-test.
- Function ARN: arn:aws:lambda:us-east-1::runtime:a0627e8616c4eaf447133f427c7419e5ce3a39ea2bc648ccb6d03d5b7f4d96e7.
- Runtime: Python 3.13. Handler: lambda_function.lambda_handler.
- Execution role: LabRole. Memory: 128 MB. Timeout: 30 giây.
- SNS_TOPIC_ARN: arn:aws:sns:us-east-1:053151184394:fooddelivery-order-events. VPC: No VPC.
- Mã nguồn: code/TanPhat/lambda_function.py.
- Tag Project: FoodDeliveryRealtime. Tag Owner: 24110298.
- Kết quả tạo và Deploy: Thành công.

### Minh chứng
- [Tên hàm TV1, runtime và handler.](../../evidence/TanPhat/Week_01/E-TV1-13_Lambda_Config.png)
- [Configuration → Permissions → Execution role LabRole.](../../evidence/TanPhat/Week_01/E-TV1-14_Lambda_LabRole.png)
- [SNS_TOPIC_ARN đúng Topic ARN.](../../evidence/TanPhat/Week_01/E-TV1-15_Lambda_Environment.png)
- [Project và Owner.](../../evidence/TanPhat/Week_01/E-TV1-16_Lambda_Tags.png)
- [Memory 128 MB và Timeout 30 giây.](../../evidence/TanPhat/Week_01/E-TV1-17_Lambda_Timeout.png)

## Kiểm thử Lambda echo và SNS
- Ngày thực hiện: 9/10/2026.
- Function: fooddelivery-foundation-test.
- Email Lambda: Đã nhận.
- CloudWatch Logs: Đã xem.

### Minh chứng
- [Execution results thành công, output echo.](../../evidence/TanPhat/Week_01/E-TV1-18_Lambda_Echo.png)
- [Execution results thành công, output SNS có messageId.](../../evidence/TanPhat/Week_01/E-TV1-19_Lambda_SNS.png)
- [Email do Lambda publish, subject và nội dung đúng.](../../evidence/TanPhat/Week_01/E-TV1-20_Lambda_SNSEmail.png)
- [CloudWatch log của hàm TV1, mode và orderId.](../../evidence/TanPhat/Week_01/E-TV1-21_Lambda_Logs.png)

## Step Functions kiểm thử Pass
- Ngày thực hiện: 9/10/2026.
- State machine: fooddelivery-foundation-test. Type: Standard.
- State machine ARN: arn:aws:states:us-east-1:053151184394:stateMachine:MyStateMachine. Execution role: LabRole.
- Definition: config/TanPhat/Week_01/01_pass.asl.json.
- Input: orderId TEST-W1-001.
- Execution ARN: arn:aws:states:us-east-1:053151184394:execution:MyStateMachine:w1-pass-01.
- Kết quả: Succeeded.
- Phạm vi: chạy workflow cơ bản, chưa chứng minh quyền gọi Lambda.

### Minh chứng
- [Tên state machine, Standard, role ARN LabRole.](../../evidence/TanPhat/Week_01/E-TV1-22_SFN_Config.png)
- [Project và Owner.](../../evidence/TanPhat/Week_01/E-TV1-23_SFN_Tags.png)
- [Execution Pass, Succeeded và output foundation.](../../evidence/TanPhat/Week_01/E-TV1-24_SFN_Pass.png)

## Step Functions kiểm thử Invoke Lambda
- Ngày thực hiện: 9/10/2026.
- Definition: config/TanPhat/Week_01/02_invoke_lambda.asl.json.
- Execution ARN: arn:aws:states:us-east-1:053151184394:execution:MyStateMachine:w1-invoke-01.
- Kết quả: Succeeded.
- Phạm vi: quyền gọi Lambda từ Step Functions.

### Minh chứng
- [Execution Invoke Succeeded và Payload của Lambda.](../../evidence/TanPhat/Week_01/E-TV1-25_SFN_Invoke.png)
- [Log Lambda đối chiếu mode echo và thời gian chạy.](../../evidence/TanPhat/Week_01/E-TV1-26_SFN_InvokeLogs.png)

## Step Functions kiểm thử callback
- Ngày thực hiện: 9/10/2026.
- Definition: config/TanPhat/Week_01/03_callback.asl.json.
- Execution ARN: arn:aws:lambda:us-east-1:053151184394:function:fooddelivery-foundation-test.
- Kết quả: Succeeded.
- Quyết định điều phối: callback.
- Phạm vi: self-callback kỹ thuật, chưa là workflow nghiệp vụ.

### Minh chứng
- [Trạng thái execution và output callback, không có taskToken.](../../evidence/TanPhat/Week_01/E-TV1-27_SFN_Callback.png)
