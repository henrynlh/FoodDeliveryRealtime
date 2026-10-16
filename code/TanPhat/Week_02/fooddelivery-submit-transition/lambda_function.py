import os
import json
import time
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sfn_client = boto3.client('stepfunctions', region_name='us-east-1')

TASKS_TABLE = os.environ.get('WORKFLOW_TASKS_TABLE', 'fooddelivery-workflow-tasks')
tasks_table = dynamodb.Table(TASKS_TABLE)

def lambda_handler(event, context):
    """
    Task A4: Tiếp nhận chuyển trạng thái, claim taskToken và gửi SendTaskSuccess
    """
    print(f"Submit transition request: {json.dumps(event)}")
    
    order_id = event.get('orderId')
    target_status = event.get('targetStatus')
    actor_id = event.get('actorId', 'DRIVER-01')
    request_id = event.get('requestId', f"req-{int(time.time())}")
    
    if not order_id or not target_status:
        return {
            "ok": False,
            "errorCode": "VALIDATION_ERROR",
            "message": "Missing orderId or targetStatus"
        }
        
    try:
        # 1. Đọc task hiện tại từ DynamoDB
        response = tasks_table.get_item(
            Key={'orderId': order_id, 'step': target_status}
        )
        task_item = response.get('Item')
        
        if not task_item:
            return {
                "ok": False,
                "errorCode": "NOT_READY",
                "message": f"Task for step {target_status} is not ready yet."
            }
            
        task_token = task_item.get('taskToken')
        current_state = task_item.get('taskState')
        
        # 2. Xử lý Idempotency (gửi lại cùng requestId)
        if current_state == 'CLAIMED' and task_item.get('requestId') == request_id:
            return {
                "ok": True,
                "status": "QUEUED",
                "message": "Request already accepted and processing."
            }
            
        # 3. Claim task có điều kiện (READY -> CLAIMED) để chống tranh chấp
        now = int(time.time())
        tasks_table.update_item(
            Key={'orderId': order_id, 'step': target_status},
            UpdateExpression="SET taskState = :claimed, actorId = :actor, requestId = :req, claimedAt = :now",
            ConditionExpression="taskState = :ready",
            ExpressionAttributeValues={
                ':claimed': 'CLAIMED',
                ':ready': 'READY',
                ':actor': actor_id,
                ':req': request_id,
                ':now': now
            }
        )
        print(f"Task {target_status} for {order_id} claimed successfully by {actor_id}.")
        
        # 4. Gửi SendTaskSuccess về Step Functions
        callback_output = {
            "orderId": order_id,
            "step": target_status,
            "actorId": actor_id,
            "requestId": request_id
        }
        
        sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps(callback_output)
        )
        print("SendTaskSuccess dispatched successfully.")
        
        return {
            "ok": True,
            "status": "QUEUED",
            "message": f"Transition to {target_status} accepted."
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            print(f"Conflict: Task {target_status} for {order_id} already claimed.")
            return {
                "ok": False,
                "errorCode": "CONFLICT",
                "message": "Another driver has already claimed this order/step."
            }
        return {
            "ok": False,
            "errorCode": "INTERNAL_ERROR",
            "message": str(e)
        }
    except Exception as ex:
        return {
            "ok": False,
            "errorCode": "INTERNAL_ERROR",
            "message": str(ex)
        }