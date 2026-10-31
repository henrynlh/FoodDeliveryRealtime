import json
from decimal import Decimal
import boto3

REGION = 'us-east-1'
ACCOUNT = '053151184394'

s = boto3.Session(region_name=REGION)
assert s.client('sts').get_caller_identity()['Account'] == ACCOUNT, f"Account mismatch, expected {ACCOUNT}"

db = s.resource('dynamodb')
oid = input('OrderId: ').strip()
order = db.Table('fooddelivery-orders').get_item(
    Key={'orderId': oid}, ConsistentRead=True).get('Item')
if not order:
    raise SystemExit(f'NOT_FOUND: Order {oid} does not exist in fooddelivery-orders')

rows = []
args = {
    'KeyConditionExpression': 'orderId = :o',
    'ExpressionAttributeValues': {':o': oid},
    'ConsistentRead': True
}
while True:
    page = db.Table('fooddelivery-workflow-tasks').query(**args)
    for t in page.get('Items', []):
        row = {k: t.get(k) for k in (
            'step', 'taskState', 'actorId', 'requestId',
            'expiresAt', 'committedVersion')}
        row['hasTaskToken'] = bool(t.get('taskToken'))
        rows.append(row)
    if not page.get('LastEvaluatedKey'):
        break
    args['ExclusiveStartKey'] = page['LastEvaluatedKey']

result = {
    'order': {k: order.get(k) for k in (
        'orderId', 'status', 'version', 'driverId',
        'workflowStatus', 'workflowEndedAt', 'executionArn')},
    'tasks': rows
}
if order.get('executionArn'):
    try:
        e = s.client('stepfunctions').describe_execution(
            executionArn=order['executionArn'])
        result['executionStatus'] = e['status']
    except Exception as exc:
        result['executionStatus'] = f"ERROR: {type(exc).__name__}"

def number(x):
    if isinstance(x, Decimal):
        return int(x) if x == int(x) else float(x)
    raise TypeError(type(x).__name__)

print(json.dumps(result, ensure_ascii=False, indent=2, default=number))

