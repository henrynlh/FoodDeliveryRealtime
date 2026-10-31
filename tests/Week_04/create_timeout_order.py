import json
import time
import uuid
from datetime import datetime, timezone
import boto3

REGION = 'us-east-1'
ACCOUNT = '053151184394'

session = boto3.Session(region_name=REGION)
assert session.client('sts').get_caller_identity()['Account'] == ACCOUNT

sfn = session.client('stepfunctions')
db = session.resource('dynamodb')
orders = db.Table('fooddelivery-orders')

main_arn = f'arn:aws:states:{REGION}:{ACCOUNT}:stateMachine:fooddelivery-order-workflow'

# Nhập mốc muốn tạo
print("=== TAO DON KIEM THU TIMEOUT ===")
print("1: Ca A (Timeout cho Nhan don - PLACED v1)")
print("2: Ca B (Timeout cho Giao hang - ACCEPTED v2)")
print("3: Ca C (Timeout cho Hoan tat - DELIVERING v3)")
choice = input("Chon ca (1, 2, hoac 3): ").strip()

oid = 'ORD-W4-TO-' + uuid.uuid4().hex[:12]
execution_name = oid
stamp = datetime.now(timezone.utc).isoformat()

# Khởi chạy execution
resp = sfn.start_execution(
    stateMachineArn=main_arn,
    name=execution_name,
    input=json.dumps({"orderId": oid})
)
execution_arn = resp['executionArn']

# Tạo item Orders ban đầu
orders.put_item(
    Item={
        'orderId': oid,
        'customerId': 'C001',
        'status': 'PLACED',
        'version': 1,
        'workflowStatus': 'RUNNING',
        'executionArn': execution_arn,
        'createdAt': stamp,
        'updatedAt': stamp
    }
)
print(f"\nDa khoi tao thanh cong don: {oid}")
print(f"Execution ARN: {execution_arn}")

# Chờ 2s để StepFunctions kích hoạt Prepare
time.sleep(2)

submit_lambda = session.client('lambda')

if choice == '1':
    print("\n-> Ca A: Don dang o PLACED v1 va cho tai PrepareAcceptedTask.")
    print("Ban chi can de yen khoang 5 phut (300 giay) de workflow timeout!")

elif choice == '2':
    print("\nDang tu dong nhan don de chuyen sang ACCEPTED v2...")
    time.sleep(3)
    # Gọi submit chuyển sang ACCEPTED
    payload = {
        "orderId": oid,
        "targetStatus": "ACCEPTED",
        "actorId": "D001",
        "requestId": "W4-SETUP-ACCEPTED-" + uuid.uuid4().hex[:8],
        "expectedVersion": 1
    }
    submit_lambda.invoke(
        FunctionName='fooddelivery-submit-transition',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    print("-> Ca B: Don da sang ACCEPTED v2 va dang cho tai PrepareDeliveringTask.")
    print("De yen khoang 5 phut de workflow timeout tai buoc giao hang!")

elif choice == '3':
    print("\nDang tu dong chuyen don sang DELIVERING v3...")
    time.sleep(3)
    # Bước 1: ACCEPTED
    payload1 = {
        "orderId": oid,
        "targetStatus": "ACCEPTED",
        "actorId": "D001",
        "requestId": "W4-SETUP-ACCEPTED-" + uuid.uuid4().hex[:8],
        "expectedVersion": 1
    }
    submit_lambda.invoke(
        FunctionName='fooddelivery-submit-transition',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload1)
    )
    time.sleep(4)
    # Bước 2: DELIVERING
    payload2 = {
        "orderId": oid,
        "targetStatus": "DELIVERING",
        "actorId": "D001",
        "requestId": "W4-SETUP-DELIVERING-" + uuid.uuid4().hex[:8],
        "expectedVersion": 2
    }
    submit_lambda.invoke(
        FunctionName='fooddelivery-submit-transition',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload2)
    )
    print("-> Ca C: Don da sang DELIVERING v3 va dang cho tai PrepareCompletedTask.")
    print("De yen khoang 5 phut de workflow timeout tai buoc hoan tat!")

print("\nHay ghi lai ma don va theo doi tren Step Functions execution nhe!")

