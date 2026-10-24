import os
import json
import time
import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
dynamodb = boto3.resource('dynamodb', region_name=REGION)

TASKS_TABLE = os.environ.get('WORKFLOW_TASKS_TABLE', 'fooddelivery-workflow-tasks')
ORDERS_TABLE = os.environ.get('ORDERS_TABLE', 'fooddelivery-orders')

tasks_table = dynamodb.Table(TASKS_TABLE)
orders_table = dynamodb.Table(ORDERS_TABLE)

def lambda_handler(event, context):
    order_id = event.get('orderId')
    step = event.get('step')
    task_token = event.get('taskToken')
    
    if not order_id or not step or not task_token:
        raise ValueError("Missing orderId, step, or taskToken")
    
    # 1. Log JSON an toàn (TUYỆT ĐỐI KHÔNG IN taskToken)
    print(json.dumps({
        "event": "PREPARE_TASK",
        "orderId": order_id,
        "step": step,
        "timestamp": int(time.time())
    }))
    
    now = int(time.time())
    # 2. Đồng bộ thời hạn 300 giây khớp với timeout của Step Functions
    expires_at = now + 300  
    
    # 3. Ghi bản ghi có điều kiện: Không ghi đè nếu task đã CLAIMED hoặc DONE
    try:
        tasks_table.put_item(
            Item={
                'orderId': order_id,
                'step': step,
                'taskToken': task_token,
                'taskState': 'READY',
                'createdAt': now,
                'expiresAt': expires_at
            },
            ConditionExpression="attribute_not_exists(taskState) OR taskState = :ready",
            ExpressionAttributeValues={
                ":ready": "READY"
            }
        )
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"Task {order_id} - {step} is already claimed/done. Skip overwrite.")
        else:
            raise exc
            
    return {
        "status": "WAITING_CALLBACK",
        "orderId": order_id,
        "step": step
    }
