import json
import uuid
from datetime import datetime, timezone
import boto3

REGION = 'us-east-1'
ACCOUNT = '053151184394'

session = boto3.Session(region_name=REGION)
sfn = session.client('stepfunctions')
orders = session.resource('dynamodb').Table('fooddelivery-orders')

main_arn = f'arn:aws:states:{REGION}:{ACCOUNT}:stateMachine:fooddelivery-order-workflow'

oid = 'ORD-W4-DUP-' + uuid.uuid4().hex[:12]
stamp = datetime.now(timezone.utc).isoformat()

resp = sfn.start_execution(
    stateMachineArn=main_arn,
    name=oid,
    input=json.dumps({"orderId": oid})
)

orders.put_item(
    Item={
        'orderId': oid,
        'customerId': 'C001',
        'status': 'PLACED',
        'version': 1,
        'workflowStatus': 'RUNNING',
        'executionArn': resp['executionArn'],
        'createdAt': stamp,
        'updatedAt': stamp
    }
)

print(f"\n-> DA TAO DON MOI DE TEST GUI LAP: {oid}")

