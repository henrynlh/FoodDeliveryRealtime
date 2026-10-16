import os
import json
import time
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
TABLE_NAME = os.environ.get('WORKFLOW_TASKS_TABLE', 'fooddelivery-workflow-tasks')
tasks_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Task A3: Lưu taskToken từ Step Functions vào DynamoDB WorkflowTasks
    """
    print(f"Prepare task event: orderId={event.get('orderId')}, step={event.get('step')}")
    
    order_id = event.get('orderId')
    step = event.get('step')
    task_token = event.get('taskToken')
    
    if not order_id or not step or not task_token:
        raise ValueError("Missing orderId, step, or taskToken")
    
    now = int(time.time())
    expires_at = now + 1800  # 30 phút hết hạn token
    
    item = {
        'orderId': order_id,
        'step': step,
        'taskToken': task_token,
        'taskState': 'READY',
        'createdAt': now,
        'expiresAt': expires_at
    }
    
    # Ghi vào DynamoDB (Không log taskToken ra console để bảo mật)
    tasks_table.put_item(Item=item)
    print(f"Successfully saved task for {order_id} - step {step} with state READY.")
    
    # Quan trọng: KHÔNG gọi send_task_success ở đây, để Step Functions tiếp tục chờ
    return {
        "status": "WAITING_CALLBACK",
        "orderId": order_id,
        "step": step
    }