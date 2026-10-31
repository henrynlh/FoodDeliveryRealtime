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
lambda_client = session.client('lambda')

main_arn = f'arn:aws:states:{REGION}:{ACCOUNT}:stateMachine:fooddelivery-order-workflow'

oid = 'ORD-W4-E2E-' + uuid.uuid4().hex[:12]
execution_name = oid
stamp = datetime.now(timezone.utc).isoformat()

print(f"=== BAT DAU KHOI TAO DON E2E: {oid} ===")

# 1. Khởi chạy Step Functions execution
resp = sfn.start_execution(
    stateMachineArn=main_arn,
    name=execution_name,
    input=json.dumps({"orderId": oid})
)
execution_arn = resp['executionArn']

# 2. Tạo record trên bảng Orders (PLACED v1)
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
print("1. Da tao don PLACED version 1.")
time.sleep(3)

# 3. Nhan don (ACCEPTED v2)
print("2. Dang nhan don (ACCEPTED)...")
resp_acc = lambda_client.invoke(
    FunctionName='fooddelivery-submit-transition',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        "orderId": oid,
        "targetStatus": "ACCEPTED",
        "actorId": "D001",
        "requestId": "W4-E2E-REQ-ACC-" + uuid.uuid4().hex[:8],
        "expectedVersion": 1
    })
)
time.sleep(4)

# 4. Bat dau giao (DELIVERING v3)
print("3. Dang bat dau giao (DELIVERING)...")
resp_del = lambda_client.invoke(
    FunctionName='fooddelivery-submit-transition',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        "orderId": oid,
        "targetStatus": "DELIVERING",
        "actorId": "D001",
        "requestId": "W4-E2E-REQ-DEL-" + uuid.uuid4().hex[:8],
        "expectedVersion": 2
    })
)
time.sleep(4)

# 5. Hoan tat don (COMPLETED v4)
print("4. Dang hoan tat don (COMPLETED)...")
resp_cmp = lambda_client.invoke(
    FunctionName='fooddelivery-submit-transition',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        "orderId": oid,
        "targetStatus": "COMPLETED",
        "actorId": "D001",
        "requestId": "W4-E2E-REQ-CMP-" + uuid.uuid4().hex[:8],
        "expectedVersion": 3
    })
)
time.sleep(3)

print(f"\n-> DA HOAN TAT LUONG E2E CHO DON: {oid}")
print(f"Execution ARN: {execution_arn}")
print("Trang thai mong doi: status=COMPLETED, version=4, executionStatus=SUCCEEDED.")

